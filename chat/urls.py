from django.urls import path
from chat.controller import views, chat_views, toggles_views


app_name = 'chat'

# urlpatterns = [
#     path("", views.index, name="index"),
#     path("vehicle/options/", views.vehicle_options, name="vehicle_options"),
#     path("vehicle/set/", views.set_vehicle, name="set_vehicle"),
#     path("response/", views.chat_response, name="chat_response"),
# ]

urlpatterns = [
    path('main/', views.main, name='main'),
    path("", toggles_views.toggles_page, name="toggles_page"),
    path("vehicle/", toggles_views.vehicle_options, name="vehicle_options"),
    path("set_vehicle/", toggles_views.set_vehicle_and_go_chat, name="set_vehicle"),
    path("response/", chat_views.chat_response, name="chat_response"),
    path("info/", chat_views.info_content, name="info"),  # ✅ 모달 Ajax용 추가
]