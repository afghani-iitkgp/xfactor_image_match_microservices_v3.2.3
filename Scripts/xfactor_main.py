import os
import random
import shutil
import json
import __root__

from flask import Blueprint
from flask import request
from flask import jsonify
from flask import render_template
from werkzeug.utils import secure_filename
from pprint import pprint



from Constants import const
from Scripts.Services.ImageMatchingServices.main_image_matching_service import Main
from Scripts.Services.AwsConnection.aws_s3_bucket_conn import AWS_S3BucketConnection
from Scripts.Services.RecommendationEngines.similar_looking_recommendations import SimilarLookingBasedRecommemendation
from Scripts.Services.RecommendationEngines.discovery_page_recommendations import DiscoverNonFacialFeaturesBasedRecommemendation
from Scripts.Services.MongoConnection.mongo_connection import MongoConn
from Scripts.Utility import utils


exception_message = '{"status":False, "status":"Server error, please contact your administrator"}'
method_error_message = '{"status": False, "message": "Method not supported!"}'



app_main = Blueprint("...kuchh bhi...", __name__)

server = "testing"
# server = "production"

#---------------------------------------------------API_LEVEL#1 (INSERT INTO TABLE#1)--------------------------------------------------------------------

@app_main.route('/app1/upload_profile_img', methods=['GET', 'POST'])
def upload_profile_img_and_embeddings():
    '''
    Objective:
       It will vectorize the input image (profile) of the user_id and then store the vectors into Table#1 into database.
       :NOTE: 1) Here primary key is 'user_id'.
              2) There could be multiple profile images for a single user_id, but only one Display profile image. Here design is only for Display pic.
              In future for multiple profile images including DisplayProfileImage, primary key will be 'user_id' and 'profile_image_id' i.e. 'object_key' or 'media_id'


    :return:
    '''
    if request.method == "POST":
        try:
            json_data = request.get_json()
            response1 = {}
            response2 = {}

            if json_data['type'] == "profile":
                profile_image_s3key = json_data['profile_image_s3key']

                aws_s3_conn_obj = AWS_S3BucketConnection(server=server)
                # json_data["profile_img_nparray"] = aws_s3_conn_obj.read_image_from_s3_bucket(profile_img_s3_objectKey)   # TODO: Add image vectors

                for root, subdirs, files in os.walk(const.profile_images_dir):
                    for file in files:
                        print("Deleting file : {}".format(file))
                        os.remove(os.path.join(root, file))

                profile_image_file_path, download_status = aws_s3_conn_obj.download_single_test_image_from_s3Bucket(s3_image_key=profile_image_s3key, dest_dir=const.profile_images_dir)


                # Local file path of preference image downloaded from S3 bucket.
                json_data['profile_image_file_path'] = profile_image_file_path

                profile_image_embedding = None

                if download_status==True:
                    img_match_main_obj = Main()
                    # result_dict_list1, profile_image_embedding = img_match_main_obj.image_matching_main_service_method(case='app1', user_data_json=json_data)
                    profile_image_embedding = img_match_main_obj.image_matching_main_service_method(case='app1', user_data_json=json_data, server=server)



                record1 = json_data
                record1['profile_image_embedding'] = profile_image_embedding

                #del record1["img_nparray"]
                record1.pop("img_nparray", None)

                if profile_image_embedding is not None:
                    mongo_conn_obj = MongoConn(server=server)
                    response1 = mongo_conn_obj.insert_profileImageVector_into_Table_1(update_profile_table1=record1)
                    response2 = mongo_conn_obj.push_newProfileImgVector_into_matchedUsersArray_table2(push_profile_table2=record1)


                return response1, response2


        except Exception as e:
            utils.logger.error("Exception occurred" + str(e))



#---------------------------------------------------API_LEVEL#2 (INSERT INTO TABLE#2)--------------------------------------------------------------------

@app_main.route('/app2/upload_preference_img', methods=['GET', 'POST'])
def upload_preference_img_and_embeddings():
    '''
    Objective:
        It will vectorize the preference image first and then find the image match with respect to all the profile images (vectorized form stored in Table#1).
        Subsequently it will store those 'image_matched' profiles w.r.t user_id and corresponding preference image he/she uploaded.
        :NOTE: Here primary key is combination of 'user_id' and 'preference_image' (media_id or media_objectKey') and 'matched_profiles' are stored as an array of objects into MongoDB.


    :return:
    '''
    if request.method == "POST":
        try:
            json_data = request.get_json()
            response = {}

            if json_data['type'] == 'preference':
                preference_image_s3key = json_data['preference_image_s3key']
                aws_s3_conn_obj = AWS_S3BucketConnection(server=server)
                # json_data["preference_img_nparray"] = aws_s3_conn_obj.read_image_from_s3_bucket(preference_img_s3_objectKey)

                for root, subdirs, files in os.walk(const.preference_images_dir):
                    for file in files:
                        print("Deleting file : {}".format(file))
                        os.remove(os.path.join(root, file))

                preference_img_file_path, download_status = aws_s3_conn_obj.download_single_test_image_from_s3Bucket(s3_image_key=preference_image_s3key, dest_dir=const.preference_images_dir)

                # Local file path of preference image downloaded from S3 bucket.
                json_data['preference_image_file_path'] = preference_img_file_path

                if download_status==True:
                    img_match_main_obj = Main()
                    result_dict_list2, preference_image_embedding = img_match_main_obj.image_matching_main_service_method(case='app2', user_data_json=json_data, server=server)

                    record2 = {}
                    # if len(result_dict_list2) > 0:
                    record2["user_id"] = json_data["user_id"]
                    record2["user_gender"] = json_data["gender"]
                    record2["preference_image_s3key"] = json_data["preference_image_s3key"]
                    record2["preference_gender"] = json_data["preference_gender"]
                    record2["preference_image_embedding"] = preference_image_embedding
                    record2["matched_users"] = result_dict_list2

                    pprint(record2)

                    mongo_obj = MongoConn(server=server)
                    response = mongo_obj.insert_matched_users_with_percentage_table2(update_data_table2=record2)

                    print(json_data['user_id'])

                    return response


        except Exception as e:
            utils.logger.error("Exception occurred" + str(e))


# -----------------------------------------------API_LEVEL#3 (SEARCH FROM TABLE_2)---------------------------------------------------------------------

@app_main.route('/app3/find_matched_users', methods=['GET', 'POST'])
def recommend_users():
    '''
    Search from Table#2 with appropriate search query.

    :return:
    '''
    try:
        if request.method == "POST":
            json_data = request.get_json()

            user_id = json_data['user_id']
            preference_image_s3key = json_data['preference_image_s3key']
            match_perc = float(json_data['match_percentage'])

            mongo_obj = MongoConn(server=server)
            lst = mongo_obj.find_matched_users_from_table2(user_id=user_id, match_percentage=match_perc, preference_image_s3key=preference_image_s3key)

            response = {}
            if len(lst) >= 1:
                response["status"] = 1
                response["message"] = "Matched users with respective percentage match"
                response["data"] = lst

            elif len(lst) == 0:
                default_users = mongo_obj.find_default_users_from_table2(user_id=user_id, match_percentage=match_perc)

                if len(default_users) >= 1:
                    response["status"] = 0
                    response["message"] = "Default recommendations as same user has not updated"
                    response["data"] = default_users
                else:
                    response["status"] = -1
                    response["message"] = "There is user found in " + const.table2_preferencesBasedMatchedProfiles
                    response["data"] = []
                    utils.logger.error("Exception occurred --- " + response["message"])

            else:
                response["status"] = -1
                response["message"] = exception_message
                response["data"] = []

            return jsonify(response)
            # return json.dumps(response)


    except Exception as e:
        utils.logger.error("Exception occurred --- " + str(e))


# -----------------------------------------------SIMILAR LOOKING RECOMMENDATIONS FOR A GIVEN USER ---------------------------------------------------------------------

# -----------------------------------------------API_LEVEL# B.01 (SHOW ALL INTERESTS TABS)---------------------------------------------------------------------

@app_main.route("/show_interest", methods=["GET", "POST"])
def show_interest():
    if request.method == "GET":
        try:
            # similar_looking_reco_obj = SimilarLookingProfilesRecommemendation()
            # interests_list = similar_looking_reco_obj.show_interests()


            interest_withCapitalized_list = {}
            for k, v in const.interests_dict.items():
                interest_withCapitalized_list[k.title()] = [x.title() for x in v]

            return interest_withCapitalized_list

        except Exception as e:
            utils.logger.exception("__Error__" + str(e))



@app_main.route("/similar_looking_profiles", methods=["GET", "POST"])
def similar_profiles():
    if request.method == "POST":
        try:
           user_json_data = request.get_json()
           user_id = user_json_data["user_id"]
           similar_looking_reco_obj = SimilarLookingBasedRecommemendation()
           similar_interests_users_list = similar_looking_reco_obj.similar_looking_interest_profiles(user_id)

           random.shuffle(similar_interests_users_list)

           response_similar_looking = {}
           response_similar_looking["data"] = similar_interests_users_list
           response_similar_looking["status"] = 1
           response_similar_looking["message"] = "successful"



           return jsonify(response_similar_looking)

        except Exception as e:
            utils.logger.exception("__Error__" + str(e))


@app_main.route("/discover_recommendation", methods=["GET", "POST"])
def discover_users_without_face_matching():
    if request.method == "POST":
        try:
           user_json_data = request.get_json()
           user_id = user_json_data["user_id"]
           discover_reco_obj = DiscoverNonFacialFeaturesBasedRecommemendation()
           discover_profiles_list = discover_reco_obj.discover_similar_interest_profiles(user_id)

           random.shuffle(discover_profiles_list)

           response_discover_profiles = {}
           response_discover_profiles["data"] = discover_profiles_list
           response_discover_profiles["status"] = 1
           response_discover_profiles["message"] = "successful"

           return jsonify(response_discover_profiles)


        except Exception as e:
            utils.logger.exception("__Error__" + str(e))