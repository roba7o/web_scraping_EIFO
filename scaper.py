from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

def scrape_country_data(*country_list):
    """
    Scrapes country-specific risk-classification and cover policy data from the EIFO website 
    and organizes it into a pandas DataFrame.

    Parameters:
    -----------
    *country_list : str
        Accepts list of countries in quotes e.g. ['india', 'japan', germany] to be unpacked.
    
    Returns:
    --------
    pd.DataFrame
        A pandas DataFrame containing the scraped data.

    """

    pre_pd_data = []  
    base_url = "https://subdomain.eifo.dk/en/countries"
    
    for country in country_list:
        url = f"{base_url}/{country.lower()}"
        print(f"url is {url}")
        
        # Obtain html country specific soup-content
        response = requests.get(url)
        country_soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract risk classification
        risk_classification_div = country_soup.find('div', class_='barometer-item--active')
        if risk_classification_div:
            risk_classification = risk_classification_div.text.strip()
        else:
            risk_classification = 'Not Rated'
        
        """
        Initilize nested dict which assigns policy-provided (width varying cells)
        for each policy-condition (4 x time dependants) for all 3 types of buyers.
        """

        cover_policy_dict = {
            "Public buyer": {
                "Guarantees without credit": "",
                "Up to 1 year": "",
                "1-5 years": "",
                "Over 5 years": ""
            },
            "Private buyer": {
                "Guarantees without credit": "",
                "Up to 1 year": "",
                "1-5 years": "",
                "Over 5 years": ""
            },
            "Bank": {
                "Guarantees without credit": "",
                "Up to 1 year": "",
                "1-5 years": "",
                "Over 5 years": ""
            }
        }
        
        #Selecting all rows (not header) of the policy table. List of html soup objects.
        buyer_rows = country_soup.select(".info-table .table--desktop .row")
        for row in buyer_rows:
            buyer_type = row.find("div", class_="cell vert-head").text
            policy_description_cells = row.find_all("div", class_="cell")[1:]  # Ignore the first cell, as it contains the vert-head cell above
            
            # Determine which policies to fill based on the width of each cell
            cell_widths = [int(cell['style'].split(':')[1].replace('%', '').strip()) for cell in policy_description_cells]
            cumul_width = 0
            policy_condition_list = list(cover_policy_dict[buyer_type].keys())
            
            for i, cell in enumerate(policy_description_cells):
                policy_text = cell.text.strip()
                cell_width = cell_widths[i]
                
                while cell_width > 0 and cumul_width < len(policy_condition_list):
                    policy_type = policy_condition_list[cumul_width]    #finds text in relative width
                    cover_policy_dict[buyer_type][policy_type] = policy_text    #assigns text to master dict (cover_policy_dict)
                    cell_width -= 20    #ensures identical assignment of grouped policies
                    cumul_width += 1    #ensures each policy-time-condition is mapped

        def combine_policies(policy_dict):
            """
            Combines consecutive periods with the same policy into a single string representation.
            
            Parameters:
            -----------
            policy_dict : dict
                A dictionary where the keys are policy conditions (time periods)
                and values are stated policies associated.]

            Returns:
            str
                String summarising and grouping the policies to avoid repeated condition periods.
                    
            """
            combined_policies = []
            previous_policy = ""
            combined_period = ""
            
            for period, policy in policy_dict.items():
                if policy == previous_policy:
                    combined_period += f" & {period}"
                else:
                    if previous_policy:
                        combined_policies.append(f"{combined_period}: {previous_policy}")
                    combined_period = period
                    previous_policy = policy
            
            if previous_policy:
                combined_policies.append(f"{combined_period}: {previous_policy}")
            
            return ' | '.join(combined_policies)

        # Simplify data by combining policies
        pre_pd_data.append({
            "Country_Name": country,
            "Country_Risk_Classification": risk_classification,
            "EIFOs_cover_policy(Public_Buyer)": combine_policies(cover_policy_dict["Public buyer"]),
            "EIFOs_cover_policy(Private_Buyer)": combine_policies(cover_policy_dict["Private buyer"]),
            "EIFOs_cover_policy (Bank)": combine_policies(cover_policy_dict["Bank"])
        })
    
    # Create DataFrame with predefined column order
    world_table_titles = [
        "Country_Name",
        "Country_Risk_Classification",
        "EIFOs_cover_policy(Public_Buyer)",
        "EIFOs_cover_policy(Private_Buyer)",
        "EIFOs_cover_policy (Bank)"
    ]
    
    df = pd.DataFrame(pre_pd_data, columns=world_table_titles)
    return df

# Example usage
list_of_countries = ['india', 'Japan', 'vietnam', 'china-people-s-republic-of'] 
df = scrape_country_data(*list_of_countries) 
# df.style.set_table_attributes('style="font-size: 12px; color: black; border: 1px solid black;"')
print(df)

file_name = '-'.join(country.lower().replace(' ', '-') for country in list_of_countries) 
file_path = os.path.join("excel_outputs", f"countries_{file_name}.xlsx")
with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Country_analysis', index=False)