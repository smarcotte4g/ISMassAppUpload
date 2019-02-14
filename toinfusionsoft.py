import csv
import pandas as pd

from infusionsoft.library import Infusionsoft
from tables import get_table

APIMAPPING = {
    'First Name': 'FirstName',
    'Last Name': 'LastName',
    'Title': 'JobTitle',
    'Email Address': 'Email',
    'Account Name': 'Company',
    'Mailing Address 1': 'StreetAddress1',
    'Mailing Address 2': 'StreetAddress2',
    'City': 'City',
    'State': 'State',
    'Zip': 'PostalCode',
    'Optional Address 1': 'Address2Street1',
    'Optional Address 2': 'Address2Street2',
    'Optional City': 'City2',
    'Optional State': 'State2',
    'Optional Zip': 'PostalCode2',
    'Account Type': 'Account Type',
    'Customer Type': 'ContactType',
    'Employees': 'Employees',
    'Industry': 'Industry',
    'Phone 1': 'Phone1',
    'Phone 2 (EXT)': 'Phone1Ext',
    'Phone 3 (Mobile)': 'Phone2',
    'Salutation': 'Title',
    'Salesperson': 'Salesperson',
    'Customer_Prospect_Dormant': 'Customer_Prospect_Dormant',
    'Service of Interest': 'Service of Interest',
}


def create_custom_field(ifs, fieldname, tablename='Contact',
                        fieldtype='Text', values=None):
    form_id = -1
    query_criteria = {'Label': fieldname, 'FormId': form_id}
    existing_fields = get_table(ifs, 'DataFormField', query_criteria)
    if existing_fields and len(existing_fields) > 1:
        raise ValueError(
            f'InfusionsoftAPIError: two custom fields with the same label: '
            f'{existing_fields[0]["Label"]}')

    existing_field = existing_fields[0] if existing_fields else None

    field = {}
    if not existing_field:
        header_id = get_custom_field_header(ifs, tablename)

        created_field = ifs.DataService(
            'addCustomField',
            tablename,
            fieldname,
            fieldtype,
            header_id)
        if isinstance(created_field, tuple) or not created_field:
            raise ValueError(
                f'InfusionsoftAPIError: custom field could not be created:'
                f'{created_field[1]}')
        field['Id'] = created_field

        field['Name'] = "_" + get_table(
            ifs,
            'DataFormField',
            {'Id': created_field},
            ['Name'])[0]['Name']

        if values:
            created_values = ifs.DataService(
                'updateCustomField',
                field['Id'],
                {'Values': values})
            if isinstance(created_values, tuple):
                raise ValueError(
                    'InfusionsoftAPIError: custom field values'
                    ' could not be added')
    else:
        field['Id'] = existing_field['Id']
        field['Name'] = '_' + existing_field['Name']

    return field


def get_custom_field_header(ifs, tablename='Contact'):
    """Checks if field exists by given fieldname
    Returns header id"""

    form_id = -1
    tab = get_table(ifs, 'DataFormTab', {'FormId': form_id})
    if not tab:
        raise ValueError(
            f'InfusionsoftAPIError: {tablename} custom '
            f'field tab does not exist')
    tab_id = tab[0]['Id']

    header = get_table(ifs, 'DataFormGroup', {'TabId': tab_id})
    if not header:
        raise ValueError(
            f'InfusionsoftAPIError: {tablename} custom '
            f'field header does not exist')
    header_id = header[0]['Id']
    return header_id

if __name__ == "__main__":
    with open('apistuff.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            appname = row['appname']
            apikey = row['apikey']
            filename = row['filename']
            # Initialize
            ifs = Infusionsoft(appname, apikey)
            df = pd.read_csv(filename)
            df = df.where(pd.notnull(df), '')
            APIMAPPING['Account Type'] = create_custom_field(
                ifs,
                'Account Type',
                fieldtype='Select',
                values=','.join(df['Account Type'].dropna().unique())
            )['Name']
            APIMAPPING['Customer Type'] = create_custom_field(
                ifs,
                'Customer Type',
                fieldtype='Select',
                values=','.join(df['Customer Type'].dropna().unique())
            )['Name']
            APIMAPPING['Employees'] = create_custom_field(
                ifs,
                'Employee Count',
                fieldtype='Text',
            )['Name']
            APIMAPPING['Industry'] = create_custom_field(
                ifs,
                'Industry',
                fieldtype='Select',
                values=','.join(df['Industry'].dropna().unique())
            )['Name']
            APIMAPPING['Salesperson'] = create_custom_field(
                ifs,
                'Salesperson',
                fieldtype='Text',
            )['Name']
            APIMAPPING['Customer_Prospect_Dormant'] = create_custom_field(
                ifs,
                'Customer/Prospect/Dormant',
                fieldtype='Select',
                values=','.join(df['Customer_Prospect_Dormant'].dropna().unique())
            )['Name']
            APIMAPPING['Service of Interest'] = create_custom_field(
                ifs,
                'Product/Solution of Interest',
                fieldtype='Select',
                values=','.join(df['Service of Interest'].dropna().unique())
            )['Name']

            df.rename(APIMAPPING,axis='columns',inplace=True)
            for contact in df.to_dict('records'):
                resp = ifs.ContactService(
                    'add',
                    contact,
                )
                if contact.get('Email'):
                    ifs.APIEmailService('optIn',contact['Email'],'FranServ Import')
                if isinstance(resp, tuple):
                    raise ValueError(
                        f'InfusionsoftAPIError: {resp}')