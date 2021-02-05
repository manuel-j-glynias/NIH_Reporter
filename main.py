import util
import openpyxl
from pathlib import Path
import csv

from clinicalTrials import get_trial_info
from references import write_references


def read_grants_file():
    xlsx_file = Path('data', 'SearchResult_Export_27Jan2021_103910.xlsx')
    wb_obj = openpyxl.load_workbook(xlsx_file)
    sheet = wb_obj.active
    col_names = []
    for column in sheet.iter_cols(1, sheet.max_column):
        col_names.append(column[0].value)
    grants = []
    for row in sheet.iter_rows(min_row=2):
        grant = {}
        for cell in row:
            grant[col_names[cell.col_idx-1]] =  util.replace_characters(cell.value)
        grants.append(grant)
    return grants


# createFundedOrganization(
# city: String!
# country: String!
# id: ID!
# name: String!
# organizationID: String!
# state: String!
# type: String
#Organization ID (IPF)	Organization Name	Organization City	Organization State	Organization Type	Organization Zip	Organization Country

def create_FundedOrganization(grant,server):
    graph_id: str = util.get_unique_id('organization_')
    s: str = f'{graph_id}: createFundedOrganization( city: \\"{grant["Organization City"]}\\",country: \\"{grant["Organization Country"]}\\", id: \\"{graph_id}\\",' \
             f'name:\\"{grant["Organization Name"]}\\",organizationID:\\"{grant["Organization ID (IPF)"]}\\",state:\\"{grant["Organization State"]}\\",type:\\"{grant["Organization Type"]}\\" ),'
    print(graph_id)
    util.send_mutation(s, server)
    return graph_id

# createNIHInstituteOrCenter(id: ID!name: String!)
def create_NIHInstituteOrCenter(name,server):
    graph_id: str = util.get_unique_id('NIH_IC_')
    s: str = f'{graph_id}: createNIHInstituteOrCenter( id: \\"{graph_id}\\", name:\\"{name}\\" ),'
    print(graph_id)
    util.send_mutation(s, server)
    return graph_id


def create_NIHGrant(grant,server,oranization_dict,ic_dict,pi_dict,core_project_dict):
    graph_id: str = util.get_unique_id('grant_')
    if grant['Total Cost'] == '':
        grant['Total Cost'] = 0
    if grant['Total Cost IC'] == '':
        grant['Total Cost IC'] = 0
    if grant['Direct Cost IC'] == '':
        grant['Direct Cost IC'] = 0
    if grant['InDirect Cost IC'] == '':
        grant['InDirect Cost IC'] = 0
    if grant['Total Cost (Sub Projects)'] == '':
        grant['Total Cost (Sub Projects)'] = 0
    lower_case_search_string = grant["Project Terms"] + ' ' + grant['Project Title']+ ' ' + grant["Contact PI / Project Leader"]
    lower_case_search_string = lower_case_search_string.lower()

    s: str = f'{graph_id}: createNIHGrant(CFDACode: \\"{grant["CFDA Code"]}\\",  FOA: \\"{grant["FOA"]}\\",  IC: \\"{grant["IC"]}\\", NIHCOVID19Response:  \\"{grant["NIH COVID-19 Response"]}\\", abstract:\\"{grant["Project Abstract"]}\\",' \
             f'activity:\\"{grant["Activity"]}\\",  applicationID:\\"{grant["Application ID"]}\\", awardNoticeDate:\\"{fix_dates(grant["Award Notice Date"])}\\", budgetEndDate:\\"{fix_dates(grant["Budget End Date"])}\\", budgetStartDate:\\"{fix_dates(grant["Budget Start Date"])}\\", ' \
             f'department:\\"{grant["Department"]}\\", directCost_IC: {grant["Direct Cost IC"]},fiscalYear:\\"{grant["Fiscal Year"]}\\",  fundingMechanism:\\"{grant["Funding Mechanism"]}\\",  ' \
             f'id: \\"{graph_id}\\", inDirectCost_IC: {grant["InDirect Cost IC"]}, nihSpendingCategorization: \\"{grant["NIH Spending Categorization"]}\\",  otherPIorProjectLeaders: \\"{grant["Other PI or Project Leader(s)"]}\\", ' \
             f'programOfficialInformation: \\"{grant["Program Official Information"]}\\", projectEndDate: \\"{fix_dates(grant["Project End Date"])}\\", projectNumber: \\"{grant["Project Number"]}\\", projectStartDate: \\"{fix_dates(grant["Project Start Date"])}\\", projectTerms: \\"{grant["Project Terms"]}\\", ' \
             f'projectTitle: \\"{grant["Project Title"]}\\", publicHealthRelevance: \\"{grant["Public Health Relevance"]}\\", serialNumber: \\"{grant["Serial Number"]}\\", studySection: \\"{grant["Study Section"]}\\", supportYear: \\"{grant["Support Year"]}\\", ' \
             f'totalCost: {grant["Total Cost"]}, totalCost_IC: {grant["Total Cost IC"]}, totalCost_SubProjects: {grant["Total Cost (Sub Projects)"]}, type:\\"{grant["Type"]}\\", lower_case_search_string:\\"{lower_case_search_string}\\" ),'
    print(graph_id)
    util.send_mutation(s, server)

    handle_organization(grant, graph_id, oranization_dict, server)
    handle_ICs(grant, graph_id, ic_dict, server)
    handle_pi(grant,graph_id,pi_dict,server)
    handle_core_project(grant,graph_id,core_project_dict,server)

    return graph_id


# createPrincipalInvestigator(
# firstName: String!
# id: ID!
# middleName: String
# personID: String!
# surname: String!)
def handle_pi(grant,graph_id,pi_dict,server):
    contactPI = grant["Contact PI / Project Leader"]
    if not contactPI in pi_dict:
        contactPI_graph_id: str = util.get_unique_id('PI_')
        toks = contactPI.split(',')
        last_name = toks[0]
        toks1 = toks[1].strip().split(' ')
        first_name = toks1[0]
        if len(toks1)>1:
            middle_name = toks1[1]
        else:
            middle_name = ''

        person_id = grant["Contact PI Person ID"]
        if (middle_name == ''):
            s = f'{contactPI_graph_id}: createPrincipalInvestigator( firstName:\\"{first_name}\\", id: \\"{contactPI_graph_id}\\", personID: \\"{person_id}\\", surname:\\"{last_name}\\" ),'
        else:
            s = f'{contactPI_graph_id}: createPrincipalInvestigator( firstName:\\"{first_name}\\", id: \\"{contactPI_graph_id}\\", middleName: \\"{middle_name}\\",personID: \\"{person_id}\\", surname:\\"{last_name}\\" ),'
        print(contactPI_graph_id)
        util.send_mutation(s, server)
        pi_dict[contactPI] = contactPI_graph_id
#         addNIHGrantContactPIorProjectLeader(contactPIorProjectLeader: [ID!]!id: ID!)
    contactPI_graph_id = pi_dict[contactPI]
    s = f'addNIHGrantContactPIorProjectLeader(id: \\"{graph_id}\\", contactPIorProjectLeader: [\\"{contactPI_graph_id}\\"])'
    util.send_mutation(s, server)


def handle_ICs(grant, graph_id, ic_dict, server):
    administeringIC = grant["Administering IC"]
    if not administeringIC in ic_dict:
        administeringIC_graph_id = create_NIHInstituteOrCenter(administeringIC, server)
        ic_dict[administeringIC] = administeringIC_graph_id
    administeringIC_graph_id = ic_dict[administeringIC]
    s = f'addNIHGrantAdministeringIC(id: \\"{graph_id}\\", administeringIC: [\\"{administeringIC_graph_id}\\"])'
    util.send_mutation(s, server)
    fundingIC = grant["Funding IC(s)"]
    if not fundingIC in ic_dict:
        fundingIC_graph_id = create_NIHInstituteOrCenter(fundingIC, server)
        ic_dict[fundingIC] = fundingIC_graph_id
    fundingIC_graph_id = ic_dict[fundingIC]
    s = f'addNIHGrantFundingIC(id: \\"{graph_id}\\", fundingIC: [\\"{fundingIC_graph_id}\\"])'
    util.send_mutation(s, server)


def handle_organization(grant, graph_id, oranization_dict, server):
    organization_name = grant["Organization Name"]
    if not organization_name in oranization_dict:
        organization_graph_id = create_FundedOrganization(grant, server)
        oranization_dict[organization_name] = organization_graph_id
    organization_graph_id = oranization_dict[organization_name]
    s = f'addNIHGrantOrganization(id: \\"{graph_id}\\", organization: [\\"{organization_graph_id}\\"])'
    util.send_mutation(s, server)


# createCoreProject(coreProjectNumber: String!id: ID!)
def handle_core_project(grant, graph_id, core_project_dict, server):
    if (grant["Serial Number"]!=''):
        core_project_number = grant["Activity"] + grant["IC"] +	grant["Serial Number"]
        if core_project_number not in core_project_dict:
            core_project_graph_id: str = util.get_unique_id('core_project_')
            core_project_dict[core_project_number] = core_project_graph_id
            s = f'createCoreProject(id: \\"{core_project_graph_id}\\", coreProjectNumber: \\"{core_project_number}\\")'
            util.send_mutation(s, server)
        core_project_graph_id = core_project_dict[core_project_number]
        s = f'addNIHGrantCoreProject(id: \\"{graph_id}\\", coreProject: [\\"{core_project_graph_id}\\"])'
        util.send_mutation(s, server)


def fix_dates(d):
    dd = ''
    if d!='':
        toks = d.split('/')
        dd = toks[2] + '-' + pad(toks[0]) + '-' + pad(toks[1])
    return dd

def pad(s):
    if len(s)==1:
        s = '0' + s
    return s


def init_server(name):
    server = name
    util.initialize_graph(server)


def read_grants(server,core_project_dict):
    oranization_dict = {}
    ic_dict = {}
    pi_dict = {}

    grants = read_grants_file()
    for grant in grants:
        create_NIHGrant(grant, server, oranization_dict, ic_dict, pi_dict, core_project_dict)

def read_publications_file():
    xlsx_file = Path('data', 'Pubhl_Export_thin.xlsx')
    wb_obj = openpyxl.load_workbook(xlsx_file)
    sheet = wb_obj.active
    col_names = []
    for column in sheet.iter_cols(1, sheet.max_column):
        col_names.append(column[0].value)
    pubs = []
    for row in sheet.iter_rows(min_row=2):
        pub = {}
        for cell in row:
            pub[col_names[cell.col_idx-1]] =  util.replace_characters(cell.value)
        pubs.append(pub)
    return pubs

def read_publications(server,core_project_dict):
    pubs = read_publications_file()
    reference_dict: dict = {}
    journal_dict: dict = {}
    author_dict: dict= {}

    counter = 0
    for pub in pubs:
        print(pub['Core Project Number'], pub['PMID'],counter)
        s, ref_id = write_references(pub['PMID'], reference_dict, journal_dict, author_dict)
        if ref_id != '':
            if s!='':
                util.send_mutation(s, server)
            core_project_number = pub['Core Project Number']
            if core_project_number in core_project_dict:
                graph_id = core_project_dict[core_project_number]
                s = f'addCoreProjectPublications(id: \\"{graph_id}\\", publications: [\\"{ref_id}\\"])'
                util.send_mutation(s, server)
            else:
                print('missing:',core_project_number)
        counter += 1

        # if counter>1000:
        #     break


#  use "pip install -r requirements.txt" to get required modules

def read_ct_file():
    trials = []
    with open('data/CT_Export_04Feb2021_064551.csv', 'r') as read_obj:
        csv_dict_reader = csv.DictReader(read_obj)
        for row in csv_dict_reader:
            ct_obj = {'core_project_number':row["Core Project Number"],'nct_id':row["ClinicalTrials.gov Identifier"]}
            trials.append(ct_obj)
    return trials

# createClinicalTrial(
# brief_summary: String!
# brief_title: String!
# conditions: [String]!
# detailed_description: String!
# drugs: [String]!
# id: ID!
# nct_id: String!
# official_title: String!
# phases: [String]!
# status: String!
# status_date: String!
# study_type: String!): String
def create_clinical_trial(ct_obj):
    graph_id: str = util.get_unique_id('clinical_trial_')
    conditions_str = ''
    for condition in ct_obj['conditions']:
        conditions_str += f'\\"{condition}\\",'
    drugs_str = ''
    for drug in ct_obj['drugs']:
        drugs_str += f'\\"{drug}\\",'
    phase_str = ''
    for phase in ct_obj['phases']:
        phase_str += f'\\"{phase}\\",'

    s: str = f'{graph_id}: createClinicalTrial( brief_summary: \\"{ct_obj["brief_summary"]}\\",brief_title: \\"{ct_obj["brief_title"]}\\", conditions: [{conditions_str}], ' \
             f'detailed_description: \\"{ct_obj["detailed_description"]}\\", drugs: [{drugs_str}], id: \\"{graph_id}\\",' \
             f'nct_id:\\"{ct_obj["nct_id"]}\\",official_title:\\"{ct_obj["official_title"]}\\",phases: [{phase_str}],' \
             f'status:\\"{ct_obj["status"]}\\", status_date:\\"{ct_obj["status_date"]}\\", study_type:\\"{ct_obj["study_type"]}\\" ),'
    print(graph_id)
    util.send_mutation(s, server)
    return graph_id


def read_clinical_trials(server, core_project_dict):
    trials = read_ct_file()
    for trial in trials:
        ct_obj = get_trial_info(trial['nct_id'])
        core_project_number = trial['core_project_number']
        core_project_graph_id = core_project_dict[core_project_number]
        print(ct_obj)
        ct_graph_id = create_clinical_trial(ct_obj)
#         addClinicalTrialCoreProject(coreProject: [ID!]!id: ID!): String
        s = f'addClinicalTrialCoreProject(id: \\"{ct_graph_id}\\", coreProject: [\\"{core_project_graph_id}\\"])'
        util.send_mutation(s, server)

if __name__ == '__main__':
    server = 'localhost'
    init_server(server)
    core_project_dict = {}
    read_grants(server,core_project_dict)
    read_clinical_trials(server,core_project_dict)
    read_publications(server,core_project_dict)



