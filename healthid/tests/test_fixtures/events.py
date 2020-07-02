
personal_event = '''
        mutation{
            createEvent(
                eventTypeId: "xaf36lbw1",
                startDate: "2019-04-06",
                endDate: "2019-04-06",
                startTime: "12:30",
                endTime: "01:30",
                eventTitle: "HealthID end of year party",
                description: "This is the party of the year"
            ){
                event{
                    id,
                    startDate,
                    endDate,
                    eventTitle,
                    description
            }
            }
            }
        '''

business_event = '''
            mutation{
                createEvent(
                    eventType: "852k75gnn",
                    startDate: "2019-04-06",
                    endDate: "2019-04-06",
                    startTime: "12:30",
                    endTime: "01:30",
                    eventTitle: "HealthID end of year party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        startDate,
                        endDate,
                        eventTitle,
                        description
                }
                }
                }
            '''

new_event = '''
                mutation{
                updateEvent(
                    id: "4",
                    eventTypeId: "xaf36lbw1",
                    startDate: "2019-04-06",
                    endDate: "2019-04-06",
                    startTime: "12:30",
                    endTime: "01:30",
                    eventTitle: "HealthID end of party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        startDate,
                        endDate,
                        eventTitle,
                        description
                }
                }
                }
            '''


def wrong_user_update_event(event_id):
    return (f'''
                mutation{{
                updateEvent(
                    id: \"{event_id}\",
                    eventTypeId: "xaf36lbw1",
                    startDate: "2019-04-06",
                    endDate: "2019-04-06",
                    startTime: "12:30",
                    endTime: "01:30",
                    eventTitle: "HealthID end of party",
                    description: "This is the party of the year"
                ){{
                    event{{
                        id,
                        startDate,
                        endDate,
                        eventTitle,
                        description
                }}
                }}
                }}
            ''')


def delete_event(event_id):
    return (f'''
                mutation{{
                    deleteEvent(
                        id: \"{event_id}\"
                        ){{
                            success
                            }}
                        }}
            ''')


view_events = '''
                query{
                    events{
                        id,
                        eventTitle,
                        startDate,
                        endDate,
                        startTime,
                        endTime,
                        description,
                        user{
                        id,
                        email
                        }
                    }
                    }
            '''


def view_event(event_id):
    return (f'''
                query{{
                    event(id: \"{event_id}\"){{
                        eventTitle,
                        startDate,
                        endDate,
                        description,
                        user{{
                        id,
                        email
                        }}
                    }}
                    }}
            ''')


view_wrong_event = '''
                query{
                    event(id: "2"){
                        eventTitle,
                        startDate,
                        endDate,
                        description,
                        user{
                        id,
                        email
                        }
                    }
                    }
            '''


def wrong_user_delete_event(event_id):
    return (f'''
                mutation{{
                    deleteEvent(
                        id: \"{event_id}\"
                        ){{
                            success
                            }}
                        }}
            ''')


outlet_event = '''
            mutation{
                createEvent(
                    eventType: "16lbwaaf3",
                    startDate: "2019-04-06",
                    endDate: "2019-04-06",
                    startTime: "12:30",
                    endTime: "01:30",
                    eventTitle: "HealthID end of year party",
                    description: "This is the party of the year"
                ){
                    event{
                        id,
                        startDate,
                        endDate,
                        eventTitle,
                        description
                }
                }
                }
            '''

event_type = '''
                mutation{
                    createEventType(
                        name: "Test Personal"
                    ){
                        eventType{
                        id
                        name
                        }
                    }
                    }
            '''

view_event_types = '''
                    query{
                        eventTypes{
                            id
                            name
                        }
                        }
                '''

wrong_event_type = '''
        mutation{
            createEvent(
                eventTypeId: "f36bw1",
                startDate: "2019-04-06",
                endDate: "2019-04-06",
                startTime: "12:30",
                endTime: "01:30",
                eventTitle: "HealthID end of year party",
                description: "This is the party of the year"
            ){
                event{
                    id,
                    startDate,
                    endDate,
                    startTime,
                    endTime,
                    eventTitle,
                    description
            }
            }
            }
        '''
