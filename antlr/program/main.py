import argparse
import subprocess

def run_terraform(command: str):
    # Ejecuta el comando terraform en la carpeta /terraform/
    subprocess.run(["terraform", command, "-auto-approve"], cwd="../../terraform")


def main():
    parser = argparse.ArgumentParser(description="Wrapper para Terraform")
    parser.add_argument('--destroy', action='store_true', help='Destruir droplet')
    args = parser.parse_args()

    if args.destroy:
        print("Ejecutando: terraform destroy -auto-approve")
        run_terraform("destroy")
    else:
        print("Ejecutando: terraform apply -auto-approve")
        run_terraform("apply")

if __name__ == "__main__":
    main()
