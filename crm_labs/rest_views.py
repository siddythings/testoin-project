# Python Imports
from random import randint
import urllib
import requests
from rest_framework.views import APIView
from application.constants import BookingStatus
from bson import ObjectId
from application.settings import DB
from crm_labs.pipeline import LabCrmPiplineServies
from crm_labs.services import BookingServices
from utilities.utility import DatetimeUtils
from application.responses import SuccessResponse, BadRequestResponse, ResourceNotFoundResponse
from users.encryptions import EncryptDecrypt, Token
from authentications.permissions import APIViewWithAuthentication


class HomeDashboard(APIViewWithAuthentication):
    def get(self, request):
        lab_id = request.headers.get("lab", None)
        aggr = LabCrmPiplineServies.home_dashboard(lab_id)
        pipline_aggr_data = list(DB.labs.aggregate(aggr))
        
        pipline_aggr_data  = pipline_aggr_data[0] if pipline_aggr_data else {}
        pipline_aggr_data.update({
            "new_booking_count": pipline_aggr_data.get("new_booking_count",0),
            "completed_booking_count": pipline_aggr_data.get("completed_booking_count",0),
            "processed_booking_count": pipline_aggr_data.get("processed_booking_count",0),
            "canceled_booking_count": pipline_aggr_data.get("canceled_booking_count",0),
        })
        return SuccessResponse(data=pipline_aggr_data, message="Home Dashboard")
        

class BookingAPIView(APIViewWithAuthentication):
    def get(self, request):
        query = request.query_params
        offset = int(query.get("offset",0))
        limit = int(query.get("limit",5))
        lab_id = request.headers.get("lab", None)
        booking_id = query.get("booking_id")
        if booking_id:
            bookings_data = DB.bookings.find_one({'booking_id': booking_id})
        else:
            bookings_data = DB.bookings.find({'lab_id': lab_id}).sort('created_at',-1).skip(offset).limit(limit)
        return SuccessResponse(data=bookings_data, message="Bookings")
    
    def post(self, request):
        # Update Status 
        query = request.query_params
        request_data = request.data
        booking_id = request_data.get("booking_id")
        if not booking_id:
            return BadRequestResponse(message="Booking ID Requried!")
        
        lab_id = request.headers.get("lab", None)
        
        bookings_update = DB.bookings.update_one({'lab_id': lab_id, 'booking_id': booking_id},{"$set":{
            "status": request_data.get("status")
        }})
        
        if not bookings_update.modified_count:
            return BadRequestResponse(message="Booking ID Not Found!")
        return SuccessResponse(data=[], message="Bookings")
    
    def patch(self, request):
        query = request.query_params
        request_data = request.data
        lab_id = request.headers.get("lab", None)
        booking_id = request_data.get("booking_id",[])
        report_file = request.FILES['file']
        
        if not booking_id:
            return BadRequestResponse(message="Booking ID Not Found!")
        
        if not report_file:
            return BadRequestResponse(message="File Not Found!")
        
        pdf_url = BookingServices.update_report(booking_id, report_file)
        print(pdf_url)
        # booking_id = query.get("booking_id")
        # if not booking_id:
        #     return BadRequestResponse(message="Booking ID Requried!")
        
        # lab_id = request.headers.get("lab", None)
        
        bookings_update = DB.bookings.update_one({'lab_id': lab_id, 'booking_id': booking_id},{"$set":{
            "status": "COMPLETED",
            "report_url": pdf_url
        }})
        
        # if not bookings_update.modified_count:
        #     return BadRequestResponse(message="Booking ID Not Found!")
        return SuccessResponse(data=[], message="Bookings")
    
    def delete(self, request):
        return SuccessResponse(data=[], message="Bookings")

class PackagesAPIView(APIViewWithAuthentication):
    def get(self, request):
        lab_id = request.headers.get("lab", None)
        packages_list = DB.packages.find({'lab_id':lab_id})
        return SuccessResponse(data=packages_list, message="Packages")
    
    def post(self, request):
        request_data = request.data
        lab_id = request.headers.get("lab", None)
        lab_details = DB.labs.find_one({'id':lab_id},{'name':1,'icon':1})
        
        # request_data.update({
        #     "lab_name": lab_details.get("name"),
        #     "lab_icon": lab_details.get("icon")
        # })
        
        request_data.update({
            "lab_name": lab_details.get("name"),
            "lab_icon": lab_details.get("icon"),
            "lab_id": lab_id,
            "is_active": False,
            "offer_price": request_data.get("mrp"),
            "created_at": DatetimeUtils.get_current_time(),
            "updated_at": DatetimeUtils.get_current_time()
        })
        
        DB.packages.insert_one(request_data)
        return SuccessResponse(data=request_data, message="Packages")

    def patch(self, request):
        request_data = request.data
        package_id = request_data.get("_id")
        request_data.pop("_id")
        if package_id:
            DB.packages.update_one({'_id': ObjectId(package_id)},{"$set":request_data})
        return SuccessResponse(data=[], message="Packages")
    
    def put(self, request):
        return SuccessResponse(data=[], message="Packages")

class AddOnServices(APIViewWithAuthentication):
    def get(self, request):
        add_on_services = DB.add_on_services.find({})
        return SuccessResponse(data=add_on_services, message="Adon")

class PackageInstructionsAPIView(APIViewWithAuthentication):
    def get(self, request):
        package_instructions = DB.package_instructions.find({})
        return SuccessResponse(data=package_instructions, message="Instructions")