import argparse
import subprocess
import json
import os
import requests

def run_terraform(command: str):
    # Ejecuta el comando terraform en la carpeta /terraform/
    subprocess.run(["terraform", command, "-auto-approve"], cwd="../../terraform")

def extraer_info_statefile(tfstate_path="../../terraform/terraform.tfstate", salida_path="../../terraform/droplet_state.json"):
    if not os.path.exists(tfstate_path):
        print("No se encontró el archivo terraform.tfstate")
        return
    with open(tfstate_path, "r") as f:
        tfstate = json.load(f)
    try:
        resources = tfstate["resources"]
        for res in resources:
            if res["type"] == "digitalocean_droplet":
                instance = res["instances"][0]
                nombre = instance["attributes"]["name"]
                droplet_id = instance["attributes"]["id"]
                ip = instance["attributes"].get("ipv4_address", "")
                with open(salida_path, "w") as out:
                    json.dump({"name": nombre, "id": droplet_id, "ip": ip}, out, indent=2)
                print(f"Archivo {salida_path} guardado correctamente.")
                return
        print("No se encontró un recurso digitalocean_droplet en el statefile.")
    except Exception as e:
        print(f"Error procesando el statefile: {e}")

def leer_droplet_state(salida_path="../../terraform/droplet_state.json"):
    if not os.path.exists(salida_path):
        print("No se encontró el archivo droplet_state.json")
        return None
    with open(salida_path, "r") as f:
        return json.load(f)

def destruir_droplet_api(droplet_id, token):
    url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print("Droplet destruido exitosamente vía API.")
    else:
        print(f"Error al destruir el droplet: {response.status_code} - {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Wrapper para Terraform")
    parser.add_argument('--destroy', action='store_true', help='Destruir droplet')
    args = parser.parse_args()

    if args.destroy:
        print("Ejecutando: destroy vía API")
        state = leer_droplet_state()
        if state is None:
            print("No se puede destruir porque no se encontró el archivo de estado.")
            return
        droplet_id = state["id"]
        token = os.environ.get("DO_TOKEN")
        if not token:
            print("Por favor, define la variable de entorno DO_TOKEN con tu token de DigitalOcean.")
            return
        destruir_droplet_api(droplet_id, token)
    else:
        print("Ejecutando: terraform apply -auto-approve")
        run_terraform("apply")
        extraer_info_statefile()

if __name__ == "__main__":
    main()
