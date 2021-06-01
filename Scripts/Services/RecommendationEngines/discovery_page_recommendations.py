from collections import defaultdict
from math import asin, pi, radians, sin, cos, sqrt, atan2
from operator import itemgetter
from Scripts.Utility import utils



from Scripts.Services.MongoConnection.mongo_connection import MongoConn
from Constants import const

class DiscoverNonFacialFeaturesBasedRecommemendation:
    def __init__(self):
        pass

    def calculate_neighbourhood_distance(self, loc1, loc2):
        #
        [lat1, lon1] = loc1
        [lat2, lon2] = loc2

        p = 0.017453292519943295  # pi/180
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        dist = 12742 * asin(sqrt(a))  # 2 * R; R = 6371 km

        return dist

        #
        # ##
        #
        # # approximate radius of earth in km
        # R = 6373.0
        #
        # lat1 = radians(loc1[0])
        # lon1 = radians(loc1[1])
        #
        # lat2 = radians(loc2[0])
        # lon2 = radians(loc2[1])
        #
        # dlon = lon2 - lon1
        # dlat = lat2 - lat1
        #
        # a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        # c = 2 * atan2(sqrt(a), sqrt(1 - a))
        #
        # distance = R * c
        #
        # print("Result:", distance)
        # print("Result 2 :", dist)


    def discover_similar_interest_profiles(self, user_id):

        '''
        Given a user find all the potential match which he/she could like to discover/explore for dating.
        Idea is to make recommendations based on:
                    1) similar interests
                    2) similar professions
                    3) staying in neighbourhood (geolocation neighbours)
                    4) User's preference for:
                        a) body_type
                        b) height
                        c) age difference
                        d) sexual orientation
        '''

        try:
            mongo_conn_obj = MongoConn()
            user_data = mongo_conn_obj.find_user_data(user_id=user_id)

            interests_list = []
            similar_interests_users_list = []

            recommended_users_discovery_page = mongo_conn_obj.mongodb_search_to_recommend_profiles_for_discovery_page(user_data)
            already_discovered_friends = mongo_conn_obj.discover_new_friends(user_id)

            for j in recommended_users_discovery_page:
                try:
                    d = {}
                    if j["user_id"] not in already_discovered_friends:
                        print(j["user_id"])
                        d["user_id"] = j["user_id"]
                        d["username"] = j["username"]
                        d["name"] = j["name"]
                        d["age"] = j["age"]
                        d["age_diff"] = abs(j["age"] - user_data["age"])
                        d["location"] = j["location"]
                        d["gender"] = j["gender"]
                        d["body_type"] = j["body_type"]
                        d["email"] = j["email"]
                        d["height"] = j["height"]
                        d["profession"] = j["profession"]

                        # j_coordinates = j["geometry"]["coordinates"]
                        d["distance"] = self.calculate_neighbourhood_distance(user_data["geometry"]["coordinates"], j["geometry"]["coordinates"])

                        for pic in j["aPhoto"]:
                            if pic["type"] == "profile" and pic["is_dp"] == True:
                                d["image"] = pic["media_url"]
                                break
                            elif pic["type"] == "profile" and pic["is_dp"] == False:
                                d["image"] = pic["media_url"]
                                break

                        similar_interests_users_list.append(d)

                except Exception as e:
                    utils.logger.exception("__Error__" + str(e))

            # newlist1 = sorted(similar_interests_users_list, key=lambda k: k['age_diff'], reverse=False) # Ascending order w.r.t distances
            mylist = sorted(similar_interests_users_list, key=itemgetter('distance', 'age_diff'), reverse=False) # Ascending order w.r.t distances and then of age_differences

            return mylist
            # for k, v in const.interests_dict.items():


        except Exception as e:
            utils.logger.exception("__Error__" + str(e))









