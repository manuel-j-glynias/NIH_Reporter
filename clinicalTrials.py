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
            if intervention['InterventionType'] == 'Drug':
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

# 'FullStudiesResponse'
if __name__ == '__main__':
    get_trial_info('NCT03271372')