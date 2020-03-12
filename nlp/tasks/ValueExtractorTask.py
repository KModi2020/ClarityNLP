from pymongo import MongoClient

from algorithms import *
from .task_utilities import BaseTask

SECTIONS_FILTER = "sections"

class ValueExtractorTask(BaseTask):
    task_name = "ValueExtractor"

    def run_custom_task(self, temp_file, mongo_client: MongoClient):
        filters = dict()
        if self.pipeline_config.sections and len(self.pipeline_config.sections) > 0:
            filters[SECTIONS_FILTER] = self.pipeline_config.sections

        denom_only = False
        if 'denom_only' in self.pipeline_config.custom_arguments:
            value = self.pipeline_config.custom_arguments['denom_only']
            if isinstance(value, str):
                if len(arg_str) > 0 and arg_str.startswith( ('T','t') ):
                    denom_only = True
                else:
                    denom_only = False
            elif isinstance(value, bool):
                denom_only = value

        values_before_terms = False
        if 'values_before_terms' in self.pipeline_config.custom_arguments:
            value = self.pipeline_config.custom_arguments['values_before_terms']
            if isinstance(value, str):
                if len(value) > 0 and value.startswith( ('T','t') ):
                    values_before_terms = True
                else:
                    values_before_terms = False
            elif isinstance(value, bool):
                values_before_terms = value
            
        # TODO incorporate sections and filters
        for doc in self.docs:
            result = run_value_extractor_full(term_list = self.pipeline_config.terms,
                                              text = self.get_document_text(doc),
                                              minimum_value = self.pipeline_config.minimum_value,
                                              maximum_value = self.pipeline_config.maximum_value,
                                              enumlist = self.pipeline_config.enum_list,
                                              is_case_sensitive_text = self.pipeline_config.case_sensitive,
                                              denom_only = denom_only,
                                              values_before_terms = values_before_terms)
            if result:
                for meas in result:
                    value = meas['X']

                    obj = {
                        "sentence": meas.sentence,
                        "text": meas.text,
                        "start": meas.start,
                        "value": value,
                        "end": meas.end,
                        "term": meas.subject,
                        "dimension_X": meas.X,
                        "dimension_Y": meas.Y,
                        "dimension_Z": meas.Z,
                        "units": meas.units,
                        "location": meas.location,
                        "condition": meas.condition,
                        "value1": meas.value1,
                        "value2": meas.value2,
                        "temporality": meas.temporality,
                        "result_display": {
                            "date": doc[util.solr_report_date_field],
                            "result_content": "{0} {1} {2}".format(meas.text, value, meas.units),
                            "sentence": meas.sentence,
                            "highlights": [meas.text, value, meas.units],
                            "start": [meas.start],
                            "end": [meas.end]
                        }
                    }
                    self.write_result_data(temp_file, mongo_client, doc, obj)

                del result
            else:
                temp_file.write("no matches!\n")
