@0xba87cf7f02d0afa5;

struct TSData {

    time @0 :UInt64;
    timeBeforeTransmit @1 :UInt64;

    accessoryBatteryVoltage @2 :Float32;
    accessoryBatteryCurrent @3 :Float32;

    fuelCellOutputVoltage @4 :Float32;
    fuelCellOutputCurrent @5 :Float32;

    supercapacitorVoltage @6 :Float32;
    supercapacitorCurrent @7 :Float32;

    motorControllerSupplyVoltage @8 :Float32;
    motorControllerSupplyCurrent @9 :Float32;

    fuelCellEnergyAccumulated @10 :Float32;

    h2PressureLow @11 :Float32;
    h2PressureFuelCell @12 :Float32;
    h2PressureHigh @13 :Float32;
    h2LeakageSensorVoltage @14 :Float32;

    fanDutyCycle @15 :Float32;
    blowerDutyCycle @16 :Float32;

    temperatureFuelCellLocation1 @17 :Float32;
    temperatureFuelCellLocation2 @18 :Float32;

    accelPedalVoltage @19 :Float32;
    brakePedalVoltage @20 :Float32;
    accelOutputVoltage @21 :Float32;
    brakeOutputVoltage @22 :Float32;

    buttonsMasterMask @23 :UInt8;
    buttonsSteeringWheelMask @24 :UInt8;

    sensorRpm @25 :Float32;
    sensorSpeed @26 :Float32;

    lapNumber @27 :UInt8;
    lapTime @28 :UInt64;

    gpsAltitude @29 :Float32;
    gpsLatitude @30 :Float32;
    gpsLongitude @31 :Float32;
    gpsSpeed @32 :Float32;

    masterState @33 :MasterOperatingState;
    protiumState @34 :ProtiumOperatingState;

    mainValveEnableOutput @35 :Bool;
    motorControllerEnableOutput @36 :Bool;

    enum MasterOperatingState {
        idle @0;
        running @1;
        shutdown @2;
        failure @3;
    }

    enum ProtiumOperatingState {
        disconnected @0;
        systemOff @1;
        firmwareVersion @2;
        commandNotFound @3;
        enteringToStartingPhase @4;
        enteringToRunningPhase @5;
        anodeSupplyPressureCheck @6;
        temperatureCheck @7;
        fcGasSystemCheck @8;
        fcSealingCheck @9;
        fcVoltageCheck @10;
        lowH2Supply @11;
        shutdownInitiated @12;
        abnormalShutdownInitiated @13;
        running @14;
    }
    
}