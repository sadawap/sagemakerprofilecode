# This code will print all users and app of sagemaker domain on terminal, as well as save the details in csv file.

import boto3
import csv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ParamValidationError

# Create a session using the default profile
session = boto3.Session(profile_name='default')

def list_sagemaker_profiles_and_apps(domain_id):
    try:
        sagemaker_client = session.client('sagemaker')

        # Initialize pagination token for user profiles
        next_token = None
        user_profiles = []

        # Paginate through all user profiles
        while True:
            if next_token:
                profiles_response = sagemaker_client.list_user_profiles(DomainIdEquals=domain_id, NextToken=next_token)
            else:
                profiles_response = sagemaker_client.list_user_profiles(DomainIdEquals=domain_id)
            
            user_profiles.extend(profiles_response.get('UserProfiles', []))
            next_token = profiles_response.get('NextToken')
            if not next_token:
                break

        # Prepare data for CSV
        csv_data = []

        # Iterate through all user profiles
        for profile in user_profiles:
            profile_name = profile['UserProfileName']

            # Initialize pagination token for apps
            app_next_token = None
            apps_found = False

            while True:
                if app_next_token:
                    apps_response = sagemaker_client.list_apps(UserProfileNameEquals=profile_name, DomainIdEquals=domain_id, NextToken=app_next_token)
                else:
                    apps_response = sagemaker_client.list_apps(UserProfileNameEquals=profile_name, DomainIdEquals=domain_id)
                
                apps = apps_response.get('Apps', [])
                app_next_token = apps_response.get('NextToken')

                if apps:
                    apps_found = True
                    for app in apps:
                        app_name = app['AppName']
                        app_status = app['Status']
                        csv_data.append([profile_name, app_name, app_status])
                if not app_next_token:
                    break

            if not apps_found:
                csv_data.append([profile_name, "No apps found", "N/A"])

        # Write data to CSV
        with open('sagemaker_profiles_and_apps.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["User Profile", "App Name", "Status"])
            writer.writerows(csv_data)

    except NoCredentialsError:
        print("Credentials not available.")
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
    except ParamValidationError as e:
        print(f"Parameter validation error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Specific SageMaker domain ID
    domain_id = 'd-myadbdpfmaoe'
    list_sagemaker_profiles_and_apps(domain_id)
