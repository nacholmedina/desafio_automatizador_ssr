import os
import json
import requests
import logging

from ClientData import ClientDataExtractor
from Validators import TokenValidation,CUITValidation
from UserAgentRotator import RandomUserAgent
from dotenv import load_dotenv

load_dotenv()

# Cargamos el Bearer token que ya obtuvimos
bearer_token = os.getenv("SKYWALKER_TOKEN")

def OfferLookup(cuit_cliente):
    client_data = ClientDataExtractor(cuit_cliente)

    if client_data == None:
        logging.warning('No hay datos para ese cliente')
        return None
    url = "https://aple.bff.bancogalicia.com.ar/api/ofertas"
    headers = {
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiJ9.eyJqdGkiOiJjMTQzNzFmYS0yMTc0LTQ0YWYtYmUwYi0zMTE0NThiNDMwZmUiLCJpYXQiOjE3MzMzNTk4MzAsImlzcyI6IlBPQ0EiLCJzdWIiOiIyMDgwMTAyIiwiYXVkIjoib2ZmaWNlYmFua2luZyIsImJyYW5jaC1pZCI6bnVsbCwiY2FwLXNjb3BlIjoiaWRlbnRpdHkiLCJjYXNoYm94LWlkIjpudWxsLCJjbGllbnQtYXR0ZW50aW9uLWlkIjpudWxsLCJjbGllbnQtZGV2aWNlLWlkIjpudWxsLCJjbGllbnQtaWQiOiJHT1JNIiwiY2xpZW50LWlwIjoiMTgxLjE3MC4yMzUuMjAiLCJjbGllbnQtc2Vzc2lvbi1pZCI6bnVsbCwiZGV2aWNlLXByaW50IjpudWxsLCJlbXBsb3llZS1pZCI6bnVsbCwiZW1wbG95ZWUtc3VwZXJ2aXNvci1pZCI6bnVsbCwiZnVuY2lvbmFsaXR5LWlkIjoiY2FwX2ltcGVyc29uYWxfbG9naW5fdjRfbG9naW4iLCJnby1pZCI6ImdsYWdnZXIwMDIiLCJnby1pZC1udW0iOiIxNjk4Mjc4IiwiaWQtYWRoZXNpb24iOiIxNjk4Mjc4IiwiaWQtaG9zdCI6IjkwMDAzMDcxNzgiLCJpZC1wZXJzb25hLXBvbSI6IjIwODAxMDIiLCJpZC11c3VhcmlvLWdvIjoiZ2xhZ2dlcjAwMiIsImlkX2NoYW5uZWwiOiJvZmZpY2ViYW5raW5nIiwiaWRfcG9tX293bmVyIjoiNTM0MDY2NCIsImlkX3BvbV91c2VyIjoiMjA4MDEwMiIsImlzLWN1c3RvbWVyIjp0cnVlLCJpcy1lbXBsb3llZSI6ZmFsc2UsImp3dC12ZXJzaW9uIjoiMy4wLjAiLCJvd25lci1kb2N1bWVudC1pZCI6IjMwNzE1MjYyNjI5Iiwib3duZXItZG9jdW1lbnQtdHlwZSI6IkNVSVQiLCJvd25lci1wZXJzb24tdHlwZSI6IkoiLCJwZXJzb24tdHlwZSI6IkYiLCJzZWdtZW50LWNvZGUiOiIwMDEyMjAwMzAiLCJzZWdtZW50LWlkIjpudWxsLCJzaW11bGF0aW9uLW1vZGUiOmZhbHNlLCJzaW5nbGUtdXNlci1tYXJrIjoiZmFsc2UiLCJ0ZXJtaW5hbC1pZCI6bnVsbCwidXNlci1kYXRhIjp7ImJpcnRoLWRhdGUiOiIwOS0wNC0xOTcxIiwiYnVzaW5lc3MtbW9kZWwiOiJleHByZXNzIiwiYnVzaW5lc3MtbmFtZSI6IldJTkNPSU4gU0EiLCJmaXJzdC1uYW1lIjoiQ0FSSU5BIEJFTEtJUyIsImdlbmRlciI6IkYiLCJpZC1hZGhlc2lvbiI6IjE2OTgyNzgiLCJpZC1jbGllbnQiOiJnbGFnZ2VyMDAyIiwiaWQtaG9zdCI6IjkwMDAzMDcxNzgiLCJpZC1wZXJzb25hLXBvbSI6IjIwODAxMDIiLCJpZF9wb21fb3duZXIiOiI1MzQwNjY0IiwiaWRfcG9tX3JlbGF0aW9uIjoiMjI0NjI1MjgiLCJpZF9wb21fdXNlciI6IjIwODAxMDIiLCJsYXN0LW5hbWUiOiJST01FUk8iLCJsb2dpbi10cmFja2luZy1pZCI6ImQ3ZDdlNzBlLTZkZjAtNDdjOS04MWY1LTE4MWFlMWNiNDRjYyIsInBvbS1vd25lci1kb2N1bWVudHMiOnsiQ1VJVCI6IjMwNzE1MjYyNjI5In0sInBvbV91c2VyX2RvY3VtZW50cyI6eyJEVSI6IjIyMTk0Mjc2IiwiQ1VJVCI6IjI3MjIxOTQyNzY2In0sInJlcXVpcmVzX2RpZ2l0YWxfc2lnbmF0dXJlIjoiZmFsc2UifSwidXNlci1kb2N1bWVudC1pZCI6IjIyMTk0Mjc2IiwidXNlci1kb2N1bWVudC10eXBlIjoiRFUiLCJ1c2VyLWlkIjoiZ2xhZ2dlcjAwMiIsImV4cCI6MTczMzM2MzQzMH0.RY0eBNUnVhsdEzHRzruTXkrBpCaZQwVQUA0s5BbdAMI0_G1IHcKkkc3LK-FaejY_iXobXnNhDzbdNCExO8xLcefjlYWwFDBgtmHy2nMKkZ2gtBQHFjvn5L9RScvqhH5wiilAGS6Z41JncYgUQP43KLo8uCS-L0RTfIOO5iwZxPgIZR9uY4ori_UTYu14wlVGbekHDFBLo9y_jHKsrTFOWjLolmYPsFZ3LEjKSKIFMnzhUpOZGa7h_QXBzERFbFiqq5VHMiO8Flkh8fy7VGDmswCAwziAymP48WBCjKhcOk8QzBUvvvniFhaR0rcbEEjMigADTqfXCOm_7EcSn0J7Lg',
        'Content-Type': 'application/json',
        'Origin': 'https://wsec06.bancogalicia.com.ar',
        'Referer': 'https://wsec06.bancogalicia.com.ar/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'cuit-tomador': cuit_cliente,
        'id-host-tomador': str(client_data['idHost']),
        'id_channel': 'officebanking',
        }

    payload = json.dumps({
        "bureau": "",
        "cuentas": [
            "CC"
                ],
                "info": {
                    "esCliente": client_data['esCliente'],
                    "esIndividuo": client_data['esIndividuo'],
                    "cuit": cuit_cliente,
                    "idActividadAFIP": str(client_data['esIndividuo'])
                }
            })

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logging.info("Intentando recuperar ofertas (intento %d)", attempt + 1)
            print(payload)
            response = requests.post(url, headers=headers, data=payload, timeout=150)
            print(response)
            return CreateJSON(response.json(),cuit_cliente)
        except requests.exceptions.Timeout:
            logging.warning("Tiempo límite de respuesta excedido %d. Reintentando...", attempt + 1)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error recuperando ofertas: {e}")
            return None

    logging.error("Max retries reached for offer lookup request. Unable to retrieve data.")
    return None

def CreateJSON(response_json, cuit):
    unique_offers = set()
    new_offer_details = []
    try:
        gondola_data = response_json.get('data', {}).get('gondola', {})
        for card in gondola_data.get('cardSDV', []):
            for product in card.get('productos', []):
                print('descripcion')
                descripcion = product.get('descripcion')
                print('montmax')
                monto_maximo = product.get('montoMaximo', 0)
                print('descripcion')
                monto_minimo = product.get('montoMinimo', 0)
                offer_key = (descripcion, monto_maximo, monto_minimo)

                if offer_key not in unique_offers and (monto_maximo > 0 or monto_minimo > 0):
                    unique_offers.add(offer_key)
                    new_offer_details.append({
                        'idOferta': product.get('idOferta'),
                        'montoMaximo': monto_maximo,
                        'montoMinimo': monto_minimo,
                        'cuotaMaxima': product.get('cuotaMaxima'),
                        'cuotaMinima': product.get('cuotaMinima'),
                        'descripcion': descripcion
                    })

        if not new_offer_details:
            logging.info(f"No valid offers for CUIT {cuit}. Skipping save.")
            return new_offer_details
        if os.path.exists('OfertasClientes'):
            with open('OfertasClientes', 'r') as json_file:
                data = json.load(json_file)
        else:
            data = {"Clients": {}}

        data["Clients"][cuit] = new_offer_details
        with open('OfertasClientes', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        final_response = {cuit: new_offer_details}


        return final_response
    except:
        logging.info(f"No valid offers for CUIT {cuit}. Skipping save.")




