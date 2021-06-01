from collections import defaultdict
from math import cos, asin, sqrt, pi
from operator import itemgetter
from Scripts.Utility import utils



from Scripts.Services.MongoConnection.mongo_connection import MongoConn
from Constants import const

class SimilarLookingBasedRecommemendation:
    def __init__(self):
        pass

    def show_interests(self):
        interest_file_path = "./Data/interests.txt"

        try:
            d = {}

            f = open(interest_file_path, "r")
            for x in f:
                interest_head = x[ : x.find(":")].lower().strip()
                interests = x[x.find(":") + 1:]
                d[interest_head] = [x.strip().lower() for x in interests.replace("\n", '').split(",")]

            return d

        except Exception as e:
            print(e)



    def similar_looking_interest_profiles(self, user_id):
        try:
            mongo_conn_obj = MongoConn()
            user_data = mongo_conn_obj.find_user_data(user_id=user_id)

            similar_interests_users_list = []

            recommended_users = mongo_conn_obj.find_profiles_having_similar_interests_spoken_languages(user_data)
            discovered_friends = mongo_conn_obj.discover_new_friends(user_id)

            for j in recommended_users:
                try:
                    d = {}
                    if j["user_id"] not in discovered_friends:
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
                        # d["distance"] = self.calculate_distance(user_coordinates, j_coordinates)

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

            newlist1 = sorted(similar_interests_users_list, key=lambda k: k['age_diff'], reverse=False) # Ascending order w.r.t distances
            # mylist = sorted(similar_interests_users_list, key=itemgetter('distance', 'age_diff'), reverse=False) # Ascending order w.r.t distances and then of age_differences

            return newlist1
            # for k, v in const.interests_dict.items():


        except Exception as e:
            utils.logger.exception("__Error__" + str(e))









