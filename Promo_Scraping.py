import hashlib
import time
import json
import requests
import pandas as pd

# Defina suas credenciais e segredo
app_id = "SUA CHAVE AQUI"  # Substitua pelo seu AppId
secret = "SUA SECRET AQUI"    # Substitua pelo seu Secret

df_final = pd.DataFrame()

# Defina o payload (corpo da requisição) como um dicionário JSON
page = 1
has_next_page = False

while page <= 50:

    payload = {
        "query": f"""
        query {{
            productOfferV2(page: {page}) {{
                nodes {{
                    productName
                    itemId
                    commissionRate
                    commission
                    price
                    sales
                    imageUrl
                    shopName
                    productLink
                    offerLink
                    periodStartTime
                    periodEndTime
                    priceMin
                    priceMax
                    productCatIds
                    ratingStar
                    priceDiscountRate
                    shopId
                    shopType
                    sellerCommissionRate
                    shopeeCommissionRate
                }}
                pageInfo {{
                    page
                    limit
                    hasNextPage
                    scrollId
                }}
            }}
        }}
        """
    }

    # Convertendo o payload em uma string JSON válida
    payload_json = json.dumps(payload)

    # Gerando o timestamp atual (em segundos)
    timestamp = str(int(time.time()))

    # Concatenando os componentes necessários para o cálculo da assinatura
    signature_base = f"{app_id}{timestamp}{payload_json}{secret}"

    # Calculando a assinatura usando SHA256
    signature = hashlib.sha256(signature_base.encode('utf-8')).hexdigest()

    # Construindo o header de autenticação
    auth_header = {
        "Authorization": f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}",
        "Content-Type": "application/json"
    }

    # URL de exemplo para a API (substitua pela URL correta da API que você deseja acessar)
    url = "https://open-api.affiliate.shopee.com.br/graphql"

    # Enviando a requisição POST com autenticação
    response = requests.post(url, headers=auth_header, data=payload_json)

    # Exibindo a resposta
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        # Supondo que a resposta seja um JSON válido:
        response_data = response.json()

        # Acessando o valor de 'hasNextPage' no JSON da resposta
        has_next_page = response_data['data']['productOfferV2']['pageInfo']['hasNextPage']

        # Verificando o valor de hasNextPage
        print(f"Has Next Page: {has_next_page}")

        if has_next_page:
            # Acessando os dados que você quer converter em DataFrame
            # Vamos supor que queremos converter os 'nodes' em um DataFrame

            page += 1

            nodes = response_data['data']['productOfferV2']['nodes']

            # Convertendo os 'nodes' em um DataFrame
            df = pd.DataFrame(nodes)

            #Juntando o daframe do nó, no dataframe final
            df_final = pd.concat([df_final,df], ignore_index=True)
        else:
            break

# Converter as colunas para tipos numéricos, forçando erros a NaN se necessário
df_final['commissionRate'] = pd.to_numeric(df_final['commissionRate'], errors='coerce')
df_final['sales'] = pd.to_numeric(df_final['sales'], errors='coerce')
df_final['ratingStar'] = pd.to_numeric(df_final['ratingStar'], errors='coerce')
df_final['priceDiscountRate'] = pd.to_numeric(df_final['priceDiscountRate'], errors='coerce')

selected_products = df_final[
    (df_final['commissionRate'] > 0.10) &
    (df_final['sales'] > 1000) &
    (df_final['ratingStar'] > 4.5) &
    (df_final['priceDiscountRate'] > 30)
]

print(selected_products)

# Exibir os produtos selecionados
selected_products_list = selected_products[['productName', 'commissionRate', 'sales', 'priceDiscountRate', 'price', 'offerLink','imageUrl']]
selected_products_list.to_csv(r'\Web_Scrap_Promo\Resumo_Promos.csv',index=False)
