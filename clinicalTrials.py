import requests
from pytrials.client import ClinicalTrials

from util import replace_characters


def get_trial_info(nct_id):
    ct = ClinicalTrials()

    full_studies = ct.get_full_studies(search_expr=nct_id, max_studies=1)

    study = full_studies['FullStudiesResponse']['FullStudies'][0]['Study']
    brief_title = study['ProtocolSection']['IdentificationModule']['BriefTitle']
    if 'OfficialTitle' in study['ProtocolSection']['IdentificationModule']:
        official_title = study['ProtocolSection']['IdentificationModule']['OfficialTitle']
    else:
        official_title = ''
    study_type = study['ProtocolSection']['DesignModule']['StudyType']
    phase_list = []
    drugs = []

    if study_type=='Interventional':
        phase_list = study['ProtocolSection']['DesignModule']['PhaseList']['Phase']
        interventions_array = study['ProtocolSection']['ArmsInterventionsModule']['InterventionList']['Intervention']
        drugs = []
        for intervention in interventions_array:
            if intervention['InterventionType'] == 'Drug' or intervention['InterventionType'] == 'Biological':
                drugs.append(intervention['InterventionName'])

    status = study['ProtocolSection']['StatusModule']['OverallStatus']
    status_date = study['ProtocolSection']['StatusModule']['StatusVerifiedDate']
    brief_summary = study['ProtocolSection']['DescriptionModule']['BriefSummary']
    if 'DetailedDescription' in study['ProtocolSection']['DescriptionModule']:
        detailed_description = study['ProtocolSection']['DescriptionModule']['DetailedDescription']
    else:
        detailed_description = ''
    conditions = study['ProtocolSection']['ConditionsModule']['ConditionList']['Condition']
    # print(brief_title,official_title,study_type,phase_list,status,status_date,brief_summary,detailed_description,conditions)
    ct_obj = {
        'nct_id':nct_id,
        'brief_title':replace_characters(brief_title),
        'official_title':replace_characters(official_title),
        'study_type': study_type,
        'phases': phase_list,
        'status':status,
        'status_date':status_date,
        'brief_summary':replace_characters(brief_summary),
        'detailed_description':replace_characters(detailed_description),
        'conditions':conditions,
        'drugs':drugs
    }
    return ct_obj

# https://clinicaltrialsapi.cancer.gov/v1/clinical-trials?size=500&include=nct_id&sites.org_postal_code=60612

def retreive_trials():
    server = "https://clinicaltrialsapi.cancer.gov/v1/clinical-trials?size=500&include=nct_id&sites.org_postal_code=60612"
    # print(server_ext)
    r = requests.get(server, headers={"Content-Type": "application/json"})
    decoded = None
    if r.ok:
        decoded = r.json()
    trials = []
    for trial_dict in decoded['trials']:
        nct = trial_dict['nct_id']
        trials.append(nct)
    return trials

# 'FullStudiesResponse'
if __name__ == '__main__':
    # trials = retreive_trials()
    # print(trials)
    # for nct in trials:
    #     info = get_trial_info(nct)
    #     print(info)
    get_trial_info('NCT03233711')
