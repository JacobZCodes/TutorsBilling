import subprocess

def findMostRecentCSV(directory): # Returns path to most recently created CSV
    command = ["powershell", "-Command", f"""Get-ChildItem -Path "{directory}" -Filter *.csv | Sort-Object CreationTime | Select-Object Name, CreationTime"""]
    result = subprocess.run(command, capture_output=True, text=True)
    command_output = result.stdout.strip().split()


    curr_csv_index = -1
    for index, item in enumerate(command_output):
        if (".csv" in item):
            curr_csv_index = index

    # Windows, if we have duplicate files we either have 'schedule2024-07-28', '(4).csv' [duplicate] or 'schedule2024-07-28.scv' [unique file]
    if ("(" in command_output[curr_csv_index]):
        csv = command_output[curr_csv_index - 1] + " " + command_output[curr_csv_index]
    else:
        csv = command_output[curr_csv_index] 
    
    path = directory + rf"\{csv}"
    return path 

def csv_to_txt(path_to_csv):
    return path_to_csv.split("\\")[-1].split(".")[0] + ".txt"

if __name__ == "__main__":
    csv_to_txt(findMostRecentCSV())

#