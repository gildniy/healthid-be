view_notifications = '''
                    query{
                        notifications{
                            id
                            subject
                            status
                            notificationMeta{
                                id
                                body
                            }
                        }
                    }
            '''

toggle_permissions = '''
                    mutation{
                        toggleEmailPermissions{
                            success,
                            errors
                        }
                        }
                '''
update_notification_status = '''
                mutation {{
                    updateNotificationStatus(id: "{notification_id}"){{
                        success
                        error
                        notification {{
                            id
                            status
                        }}
                    }}
                }}
'''

delete_notification = '''
                mutation {{
                    deleteNotification(id: "{notification_id}"){{
                        success
                        error
                    }}
                }}
'''
