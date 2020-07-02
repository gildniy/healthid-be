create_price_survey = '''
                        mutation {{
                            createPriceCheckSurvey(
                                name: "{name}",
                                outletId: {outlet_id},
                                suppliers: ["{suppliers}"],
                                products: [{products}],
                            ){{
                                success
                                survey {{
                                    id
                                    name
                                    }}
                                }}
                            }}
                        '''

delete_price_survey = '''
                mutation {{
                    deletePriceCheckSurvey(surveyId: "{survey_id}"){{
                        success
                    }}
                }}
                '''

update_price_survey = '''
                mutation {{
                    updatePriceCheckSurvey(
                        surveyId: "{survey_id}",
                        name: "{name}",
                        suppliers:["{suppliers}"],
                        products:[{products}]
                    ){{
                        success
                        survey{{
                            name
                        surveyPriceChecks {{
                            id
                            product {{
                            productName
                            }}
                            supplier {{
                            name
                            }}
                        }}
                        }}
                }}
            }}
        '''
update_price_survey_without_products = '''
                mutation {{
                    updatePriceCheckSurvey(
                        surveyId: "{survey_id}",
                        name: "{name}",
                        suppliers:["{suppliers}"]
                    ){{
                        success
                        survey{{
                            name
                        surveyPriceChecks {{
                            id
                            product {{
                            productName
                            }}
                            supplier {{
                            name
                            }}
                        }}
                        }}
                }}
            }}
        '''

update_price_survey_without_suppliers = '''
                mutation {{
                    updatePriceCheckSurvey(
                        surveyId: "{survey_id}",
                        name: "{name}",
                        products:[{products}]
                    ){{
                        success
                        survey{{
                            name
                        surveyPriceChecks {{
                            id
                            product {{
                            productName
                            }}
                            supplier {{
                            name
                            }}
                        }}
                        }}
                }}
            }}
        '''

get_price_survey = '''
            query {{
                priceCheckSurvey(id: "{survey_id}"){{
                    id
                    name
                    surveyPriceChecks {{
                    product{{
                        productName
                    }}
                    supplier{{
                        name
                    }}
                    price
                    }}
                }}
            }}
        '''

get_all_price_surveys = '''
                query {
                priceCheckSurveys {
                    id
                    name
                    surveyClosed
                    surveyPriceChecks {
                    id
                    supplier{
                        name
                    }
                    price
                    }
                }
                }
            '''
