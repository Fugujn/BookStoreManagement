from MainApp import dao
import cloudinary.uploader


def save_picture(form_picture):
    response = cloudinary.uploader.upload(form_picture)
    return response['secure_url']


def extract_search_user_by_phone(kw, max=5):
    list_user = dao.search_user_by_phone(kw, max)
    print(list_user)
    result = []
    for user in list_user:
        result.append({
            "name": user.first_name + " " +  user.last_name,
            "phone": user.phone_number
        })
    return result