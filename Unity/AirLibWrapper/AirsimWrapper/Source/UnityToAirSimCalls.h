//#pragma once

#include <thread>
#include "UnityUtilities.hpp"
#include "SimHUD/SimHUD.h"
#include "Logger.h"
#include "common/common_utils/Utils.hpp"

#ifdef _WIN32
	#define EXPORT __declspec(dllexport)
#else
	#define EXPORT __attribute__((visibility("default")))
#endif

static SimHUD* key = nullptr;

void StartServerThread(std::string vehicle_name, std::string sim_mode_name, int port_number);

extern "C" EXPORT bool StartServer(char* vehicle_name, char* sim_mode_name, int port_number)
{
	LOGGER->WriteLog("Starting server for : " + std::string(sim_mode_name));
	std::thread server_thread(StartServerThread, vehicle_name, sim_mode_name, port_number);
	server_thread.detach();
	int waitCounter = 25; // waiting for maximum 5 seconds to start a server.
	while ((key == nullptr || !key->server_started_Successfully_) && waitCounter > 0)
	{
		std::this_thread::sleep_for(std::chrono::milliseconds(200));
		waitCounter--;
	}
	return key->server_started_Successfully_;
}

extern "C" EXPORT void StopServer(char* vehicle_name)
{
	key->EndPlay();
	if (key != nullptr)
	{
		delete key;
		key = nullptr;
	}
		LOGGER->WriteLog("Server stopped");
}

extern "C" EXPORT void CallTick(float deltaSeconds)
{
	key->Tick(deltaSeconds);
}

extern "C" EXPORT void InvokeCollisionDetection(AirSimUnity::AirSimCollisionInfo collision_info)
{
	auto simMode = key->GetSimMode();
	if (simMode)
	{
		auto vehicleApi = simMode->getVehicleSimApi(simMode->vehicle_name_);
		if (vehicleApi)
		{
			msr::airlib::CollisionInfo collisionInfo = UnityUtilities::Convert_to_AirSimCollisioinInfo(collision_info);
			vehicleApi->OnCollision(collisionInfo);
		}
	}
}





extern "C" EXPORT  void  ConvertNetToGeo(msr::airlib::Vector3r rectpoints[4], msr::airlib::GeoPoint geoPoints[4])
{
	int i = 0;
	msr::airlib::Vector3r	vPoint1 = rectpoints[0];
	msr::airlib::Vector3r	vPoint2 = rectpoints[1];
	msr::airlib::Vector3r	vPoint3 = rectpoints[2];
	msr::airlib::Vector3r	vPoint4 = rectpoints[3];
	
	msr::airlib::GeoPoint geo1 = msr::airlib::EarthUtils::nedToGeodetic(vPoint1, msr::airlib::AirSimSettings::singleton().origin_geopoint);
	msr::airlib::GeoPoint geo2 = msr::airlib::EarthUtils::nedToGeodetic(vPoint2, msr::airlib::AirSimSettings::singleton().origin_geopoint);
	msr::airlib::GeoPoint geo3 = msr::airlib::EarthUtils::nedToGeodetic(vPoint3, msr::airlib::AirSimSettings::singleton().origin_geopoint);
	msr::airlib::GeoPoint geo4 = msr::airlib::EarthUtils::nedToGeodetic(vPoint4, msr::airlib::AirSimSettings::singleton().origin_geopoint);

	geoPoints[0] = geo1;
	geoPoints[1] = geo2;
	geoPoints[2] = geo3;
	geoPoints[3] = geo4;

}


