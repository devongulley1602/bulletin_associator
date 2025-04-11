#!/bin/bash
# Prints a list of URLs associated with 

# Set the base URL
base_url="https://dd.weather.gc.ca/bulletins/alphanumeric/"

# Function to process a directory
process_dir() {
    local dir_url="$1"
    
    # Names of bulletin we're looking for, in this case only WO and WW
    for var_name in 'WO' 'WW' 'AW' 'WF' 'WU'; do 
        # Check if the directory exists
        if curl -s --head --request GET "${dir_url}${var_name}/" | grep "200 OK" > /dev/null; then

            # Check if the CWUL directory exists
            if curl -s --head --request GET "${dir_url}${var_name}/CWUL/" | grep "200 OK" > /dev/null; then

                # Get the list of directories in the CWUL directory
                local dirs=$(curl -s "${dir_url}${var_name}/CWUL/" | grep -oP '(?<=href=")[^"]*(?=/")')
                for d in $dirs; do

                    # Get the list of files in the directory
                    local files=$(curl -s "${dir_url}${var_name}/CWUL/$d/" | grep -oP '(?<=href=")[^"]*(?=")')
                    for f in $files; do
                        # Only process files that have "___" present in the file name
                        if [[ "$f" == *___* ]]; then

                            # Print the file's full path URL
                            printf "${dir_url}${var_name}/CWUL/$d/$f\n" 
                        fi
                    done
                done
            fi
        fi
    done
}

# Get the list of directories in the base URL within the alotted time period
get_list() {
    local dirs=$(curl -s "$base_url" | grep -oP '(?<=href=")[^"]*(?=/")') 
    time_frame=$(echo $dirs | grep -Eo $1) # Directories sent to get_list in the form where $1 is '20250228|20250212|20250102' for example

    # Process each directory
    for d in $time_frame; do
        process_dir "${base_url}${d}/"
    done
}

get_list $1 # Argument is formatted_range which is passed from bulletin_associator.py in the form '20250228|20250212|20250102' for example
