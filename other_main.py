import re
import os
import subprocess

def remove_ansi_escape(text):
    ansi_escape_pattern = re.compile(r'\x1B\[[0-?9;]*[mG]')
    return ansi_escape_pattern.sub('', text)

result = subprocess.run(['terraform', 'plan'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

plan_output = remove_ansi_escape(result.stdout)

if 'Error' in plan_output:
    print("Erro ao executar o comando terraform plan.")

if 'aws_dynamodb_table' in plan_output:
        print("Recursos aws_dynamodb_table encontrados no plano:\n")

        list_of_dynamodb_tables = []

        lines = plan_output.splitlines()

        for line in lines:
            if 'aws_dynamodb_table' in line:
                if 'module.' in line:
                    module_name = line.split('.')[1]
                    list_of_dynamodb_tables.append({'module': module_name})

                elif 'aws_dynamodb_table.' in line:
                    resource_name = line.split('.')[1].split(' ')[0]
                    list_of_dynamodb_tables.append({'resource': resource_name})

        terraform_files = [f for f in os.listdir('.') if f.endswith('.tf')]

        list_files = []

        for file in terraform_files:
            with open(file, 'r') as f:
                content = f.read()
                for table in list_of_dynamodb_tables:
                    if 'module' in table:
                        if "\"" + table['module'] + "\"" in content:
                            print(f"Módulo {table['module']} em {file} tenta criar uma tabela DynamoDB.")
                            list_files.append(file)
                    elif 'resource' in table:
                        if "\"" + table['resource'] + "\"" in content:
                            print(f"Recurso {table['resource']} encontrado no arquivo {file}.")
                            list_files.append(file)
        
        print("\nArquivos que contêm recursos aws_dynamodb_table:")
        for file in list_files:
            print(file)
        


