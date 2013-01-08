Search.setIndex({titles:["Controllers","<tt class=\"docutils literal docutils literal\"><span class=\"pre\">openxc-control</span></tt> options and arguments","<tt class=\"docutils literal docutils literal\"><span class=\"pre\">openxc-dump</span></tt> options and arguments","Units","Measurements","Data Formats","Common interface options","OpenXC for Python","Vehicle functions","Utils","<tt class=\"docutils literal docutils literal\"><span class=\"pre\">openxc-gps</span></tt> options and arguments","Data Sinks","<tt class=\"docutils literal docutils literal docutils literal\"><span class=\"pre\">openxc-trace-split</span></tt> options and arguments","<tt class=\"docutils literal docutils literal\"><span class=\"pre\">openxc-dashboard</span></tt> options and arguments","Data Sources"],objtypes:{"0":"std:option","1":"py:module","2":"py:attribute","3":"py:function","4":"py:classmethod","5":"py:class","6":"py:exception"},objects:{"":{"--format":[10,0,1,"cmdoption--format"],"--file":[1,0,1,"cmdoption--file"],"--serial-baudrate":[10,0,1,"cmdoption--serial-baudrate"],"--corrupted":[2,0,1,"cmdoption--corrupted"],"-s":[12,0,1,"cmdoption-s"],"--serial-port":[10,0,1,"cmdoption--serial-port"],"--usb":[10,0,1,"cmdoption--usb"],"--trace":[10,0,1,"cmdoption--trace"],"--usb-vendor":[10,0,1,"cmdoption--usb-vendor"],"--name":[1,0,1,"cmdoption--name"],"--serial":[10,0,1,"cmdoption--serial"],"--value":[1,0,1,"cmdoption--value"]},"openxc.measurements":{NumericMeasurement:[4,5,1,""],FineOdometer:[4,5,1,""],BrakePedalStatus:[4,5,1,""],LateralAcceleration:[4,5,1,""],ParkingBrakeStatus:[4,5,1,""],FuelConsumed:[4,5,1,""],PercentageMeasurement:[4,5,1,""],BooleanMeasurement:[4,5,1,""],StatefulMeasurement:[4,5,1,""],SteeringWheelAngle:[4,5,1,""],FuelLevel:[4,5,1,""],TransmissionGearPosition:[4,5,1,""],UnrecognizedMeasurementError:[4,6,1,""],Odometer:[4,5,1,""],EngineSpeed:[4,5,1,""],WindshieldWiperStatus:[4,5,1,""],TurnSignalStatus:[4,5,1,""],Measurement:[4,5,1,""],AcceleratorPedalPosition:[4,5,1,""],VehicleSpeed:[4,5,1,""],TorqueAtTransmission:[4,5,1,""],Longitude:[4,5,1,""],EventedMeasurement:[4,5,1,""],HeadlampStatus:[4,5,1,""],GearLevelPosition:[4,5,1,""],DoorStatus:[4,5,1,""],HighBeamStatus:[4,5,1,""],LongitudinalAcceleration:[4,5,1,""],ButtonEvent:[4,5,1,""],NamedMeasurement:[4,5,1,""],Latitude:[4,5,1,""],IgnitionStatus:[4,5,1,""]},"openxc.measurements.Longitude":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.sources.serial.SerialDataSource":{DEFAULT_BAUDRATE:[14,2,1,""],DEFAULT_PORT:[14,2,1,""]},"openxc.controllers.usb":{UsbControllerMixin:[0,5,1,""]},"openxc.sinks.notifier":{MeasurementNotifierSink:[11,5,1,""]},"openxc.measurements.EventedMeasurement":{DATA_TYPE:[4,2,1,""]},"openxc.controllers.serial.SerialControllerMixin":{write_bytes:[0,3,1,""]},"openxc.utils.Range":{within_range:[9,3,1,""],spread:[9,2,1,""]},"openxc.sinks.uploader":{UploaderSink:[11,5,1,""]},"openxc.measurements.Odometer":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.measurements.LateralAcceleration":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.controllers.serial":{SerialControllerMixin:[0,5,1,""]},"openxc.measurements.Latitude":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.measurements.StatefulMeasurement":{states:[4,2,1,""],DATA_TYPE:[4,2,1,""],valid_state:[4,3,1,""]},"openxc.utils.AgingData":{age:[9,2,1,""]},"openxc.controllers.base":{ControllerError:[0,6,1,""],Controller:[0,5,1,""]},"openxc.measurements.TransmissionGearPosition":{states:[4,2,1,""],name:[4,2,1,""]},"openxc.measurements.IgnitionStatus":{states:[4,2,1,""],name:[4,2,1,""]},"openxc.sources.trace.TraceDataSource":{run:[14,3,1,""]},"openxc.sources.usb":{UsbDataSource:[14,5,1,""]},"openxc.sinks.recorder.FileRecorderSink.Recorder":{run:[11,3,1,""]},"openxc.measurements.WindshieldWiperStatus":{name:[4,2,1,""]},"openxc.sinks.recorder.FileRecorderSink":{Recorder:[11,5,1,""],FILENAME_DATE_FORMAT:[11,2,1,""],FILENAME_FORMAT:[11,2,1,""]},"openxc.vehicle":{Vehicle:[8,5,1,""]},"openxc.formats.json":{JsonFormatter:[5,5,1,""]},"openxc.measurements.FineOdometer":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.sources":{trace:[14,1,1,""],base:[14,1,1,""],usb:[14,1,1,""],serial:[14,1,1,""]},"openxc.sources.serial":{SerialDataSource:[14,5,1,""]},"openxc.sinks.notifier.MeasurementNotifierSink":{register:[11,3,1,""],Notifier:[11,5,1,""],unregister:[11,3,1,""]},"openxc.units":{Degree:[3,2,1,""],Kilometer:[3,2,1,""],RotationsPerMinute:[3,2,1,""],Undefined:[3,2,1,""],Meter:[3,2,1,""],Hour:[3,2,1,""],Litre:[3,2,1,""],NewtonMeter:[3,2,1,""],MetersPerSecondSquared:[3,2,1,""],KilometersPerHour:[3,2,1,""],Percentage:[3,2,1,""]},"openxc.sinks.notifier.MeasurementNotifierSink.Notifier":{run:[11,3,1,""]},"openxc.measurements.Measurement":{unit:[4,2,1,""],name_from_class:[4,4,1,""],DATA_TYPE:[4,2,1,""],value:[4,2,1,""],from_dict:[4,4,1,""]},"openxc.sinks.queued":{QueuedSink:[11,5,1,""]},"openxc.measurements.EngineSpeed":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.utils":{Range:[9,5,1,""],AgingData:[9,5,1,""]},"openxc.sources.base":{DataSourceError:[14,6,1,""],BytestreamDataSource:[14,5,1,""],DataSource:[14,5,1,""]},"openxc.sinks.queued.QueuedSink":{receive:[11,3,1,""]},"openxc.measurements.FuelLevel":{name:[4,2,1,""]},"openxc.sources.trace":{TraceDataSource:[14,5,1,""]},"openxc.measurements.AcceleratorPedalPosition":{name:[4,2,1,""]},"openxc.sinks.recorder":{FileRecorderSink:[11,5,1,""]},"openxc.measurements.VehicleSpeed":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.sinks":{notifier:[11,1,1,""],uploader:[11,1,1,""],recorder:[11,1,1,""],base:[11,1,1,""],queued:[11,1,1,""]},"openxc.measurements.GearLevelPosition":{states:[4,2,1,""],name:[4,2,1,""]},"openxc.measurements.PercentageMeasurement":{unit:[4,2,1,""],valid_range:[4,2,1,""]},"openxc.measurements.HeadlampStatus":{name:[4,2,1,""]},"openxc.measurements.ButtonEvent":{name:[4,2,1,""]},"openxc.measurements.ParkingBrakeStatus":{name:[4,2,1,""]},"openxc.controllers.usb.UsbControllerMixin":{reset:[0,3,1,""],write_bytes:[0,3,1,""],version:[0,3,1,""],out_endpoint:[0,2,1,""]},"openxc.measurements.BrakePedalStatus":{name:[4,2,1,""]},"openxc.sinks.uploader.UploaderSink.Uploader":{run:[11,3,1,""]},"openxc.measurements.HighBeamStatus":{name:[4,2,1,""]},"openxc.measurements.BooleanMeasurement":{DATA_TYPE:[4,2,1,""]},"openxc.measurements.TurnSignalStatus":{name:[4,2,1,""]},"openxc.sinks.uploader.UploaderSink":{HTTP_TIMEOUT:[11,2,1,""],Uploader:[11,5,1,""],UPLOAD_BATCH_SIZE:[11,2,1,""]},"openxc.measurements.SteeringWheelAngle":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.measurements.TorqueAtTransmission":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.controllers":{base:[0,1,1,""],usb:[0,1,1,""],serial:[0,1,1,""]},"openxc.measurements.DoorStatus":{states:[4,2,1,""],name:[4,2,1,""]},"openxc.formats.json.JsonFormatter":{deserialize:[5,4,1,""],serialize:[5,4,1,""]},"openxc.controllers.base.Controller":{write_raw:[0,3,1,""],reset:[0,3,1,""],write:[0,3,1,""],write_bytes:[0,3,1,""],version:[0,3,1,""]},"openxc.measurements.NumericMeasurement":{valid_range:[4,2,1,""],within_range:[4,3,1,""]},"openxc.sources.usb.UsbDataSource":{DEFAULT_READ_TIMEOUT:[14,2,1,""],DEFAULT_VENDOR_ID:[14,2,1,""],DEFAULT_PRODUCT_ID:[14,2,1,""],RESET_CONTROL_COMMAND:[14,2,1,""],VERSION_CONTROL_COMMAND:[14,2,1,""],DEFAULT_READ_REQUEST_SIZE:[14,2,1,""]},"openxc.sources.base.BytestreamDataSource":{run:[14,3,1,""]},"openxc.measurements.LongitudinalAcceleration":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]},"openxc.formats":{json:[5,1,1,""]},"openxc.vehicle.Vehicle":{get:[8,3,1,""],add_source:[8,3,1,""],add_sink:[8,3,1,""],unlisten:[8,3,1,""],listen:[8,3,1,""]},"openxc.sinks.base.DataSink":{receive:[11,3,1,""]},openxc:{utils:[9,1,1,""],measurements:[4,1,1,""],units:[3,1,1,""],vehicle:[8,1,1,""]},"openxc.sinks.base":{DataSink:[11,5,1,""]},"openxc.measurements.FuelConsumed":{unit:[4,2,1,""],valid_range:[4,2,1,""],name:[4,2,1,""]}},terms:{between:[0,9],acceleratorpedalposit:4,background:14,allow:1,windshield_wiper_statu:4,grab:4,version:[0,1,7],look:12,approxim:14,override_unit:4,loop:14,environ:7,upload_batch_s:11,notif:11,"default":[10,1,2,6,12,13,14],turnsignalstatu:4,futur:[4,7],serialcontrollermixin:0,add_sourc:8,"return":[8,4,0,9],primari:7,arg:[4,0,11],visit:7,select:10,libusb:7,lateralacceler:4,absolut:14,hour:[12,3],logic:12,privileg:7,defin:[0,4,13,3,9,14],headlampstatu:4,sourc:[0,1,11,6,7,8,10,2,13,14],highbeamstatu:4,queue:11,dict:[4,11],baudrat:[10,1,2,6,13,14],litr:3,steering_wheel_angl:[4,2],easy_instal:7,support:[10,1],goe:13,doe:4,name:[10,1,4,0,12,13],ignition_statu:4,other:[8,10,9,14],report:7,brake_pedal_statu:4,min:[4,9],maximum:9,you:[1,13,7],show:13,handl:11,see:[13,14,7],serial:[10,1,6,5,0,2,13,14],minimum:[9,11],latitud:[4,10],manipul:7,licens:7,python:[8,4,7],cach:4,openxcplatform:[14,7],everi:[12,11],store:11,"public":13,lateral_acceler:4,grep:2,them:[12,7],separ:[0,1,14],help:[10,1,13,2,12],about:7,column:13,everyth:2,stop:[8,14,11],collect:12,refactor:0,rear_right:4,namedcomposedunit:4,coerc:4,tar:7,variabl:4,pacman:7,"float":4,passeng:4,under:7,vehiclespe:4,transmission_gear_posit:4,todo:[0,11],data_remain:11,jsonformatt:5,implement:[0,14,11],given:[8,4,0,14],construct:[8,4,14],guid:7,sport:4,libusbx:7,servic:11,view:2,api:[10,7],need:[8,14],unrecogn:4,rotat:4,doorstatu:4,from:[10,11,4,7,8,2,14],programat:8,virtual:[10,1,2,0,6,13,14],except:[4,0,14],"function":[8,4,14,7],"class":[0,1,11,4,5,9,8,10,2,12,13,14],full:14,plain:4,listen:[8,11],request:[8,0,1,12,11],measurement_class:[8,4,11],apt:7,whenev:[8,14,11],incom:11,leafunit:4,mondai:[12,13,2],"_read":14,object:4,desir:10,html:14,valid_st:4,specif:1,devic:[14,0,13,2],valid_rang:4,same:[13,14],copyright:7,window:13,previous:[10,1,11,4,6,7,8,2,12,13,14],end:0,web:[11,7],subclass:[4,14,11],directori:12,prototyp:7,motor:[10,1,2,7,6,13],git:7,last:[13,7],devel:7,data_typ:4,differ:[12,13,2],meterspersecondsquar:3,download:7,fuel_consumed_since_restart:4,assum:2,org:7,discret:14,torqueattransmiss:4,level:4,modul:8,valu:[0,1,4,9,8,11,13],synchron:8,instal:7,unlisten:8,"0x7fa41cb9b090":4,overal:13,bah:0,unrecognizedmeasurementerror:4,non:14,seri:14,"true":[14,4,9,11],callback:[8,14,11],virtualenv:7,datasink:[8,11],thi:[0,1,11,4,6,9,8,10,2,12,13,14],tutori:7,alia:4,signal:0,back:[8,0,1,13,2],provid:[8,1,14,7],continu:14,contain:[8,0,9,7],suggest:7,thu:4,accelerator_pedal_posit:4,undefin:3,rover:4,incorrectli:13,default_read_request_s:14,fuellevel:4,pre:[10,1,4,2,12,13,14],filerecordersink:11,sixth:4,neutral:4,could:[0,14],write:[0,1],termin:13,constructor:4,queuedsink:11,"0x7fa41cb98ed0":4,trace:[10,1,11,6,7,2,12,13,14],exclus:[6,10,1,13,2],current:[4,10,1,13,7],most:[8,12],string:4,composedunit:4,"int":14,displai:13,"0x7fa41cb98e50":4,secondari:8,gener:[4,7],member:4,windshieldwiperstatu:4,avoid:4,part:8,"new":[8,4,12,14,11],"abstract":[0,14],rais:[4,14],read:[4,12,14,2,7],split:[12,7],least:[8,4,0],popular:10,namedmeasur:4,self:[0,4,8,11,9,14],remot:11,list:[12,13,7],daemon:14,alreadi:8,"0x7fa41cb98f50":4,tall:13,screenshot:13,default_port:14,park:4,sub:[8,4],pypi:7,parkingbrakestatu:4,longitud:[4,10],left:1,wider:13,serialdatasourc:14,second:[4,9],format:[10,5,7,0,11,14],parking_brake_statu:4,newtonmet:3,platform:[1,7],directli:8,attach:[6,10,1,13,2],message_id:0,"byte":[0,14],avail:[11,7],encapsul:[4,9],each:[13,2],contribut:7,statefulmeasur:4,first:[4,12,7],where:12,chang:12,"0x7fa41cb98cd0":4,data:[0,1,11,4,5,6,7,8,9,10,2,12,13,14],etc:4,overhead:7,curs:13,transmissiongearposit:4,regist:[8,11],nativ:7,thei:14,fineodomet:4,tool:[10,1,2,7,6,12,13],endpoint:[0,14],off:[4,14],url:11,print:[10,1,2],project:7,host:7,clone:7,open:[13,14],realtim:14,gpx:10,effect:[10,1,11,6,8,2,13],kind:0,gui:13,wasn:11,often:[12,7],product:14,percentagemeasur:4,associ:[4,9],filenam:14,all:[10,1,11,4,6,8,2,12,13,14],ani:[14,13,11,7],exist:14,follow:7,torque_at_transmiss:4,vendor:[10,1,2,6,13,14],choic:[10,12],packag:7,set:[10,1,6,4,8,2,13,14],oper:11,creat:4,librari:[8,7],origin:[12,11],user:[8,7],sent:13,steeringwheelangl:4,"0x7fa41cb98dd0":4,high_beam_statu:4,offici:13,default_read_timeout:14,when:[1,14,7],inform:10,send:[8,0,1,11],note:1,usbdatasourc:14,"0x7fa41cb9b110":4,rate:13,version_control_command:14,method:[8,4,0,14,11],startabl:8,filename_format:11,buffer:14,default_vendor_id:14,execut:7,str:[4,14,11],truncat:13,want:8,crash:4,sink:[8,11,7],annoy:7,includ:[4,10],record:[10,1,11,6,7,2,12,13,14],relationship:0,bytestreamdatasourc:14,classmethod:[4,5],out:[0,13],requir:[14,4,1,13,2],rear_left:4,discuss:7,fals:4,few:10,act:0,attempt:[14,2],within_rang:[4,9],post:11,degre:[4,3],com:[10,1,2,7,6,13,14],matter:14,http_timeout:11,agingdata:9,combin:12,implemtn:0,valid:[4,14,2],ignitionstatu:4,size:12,rotationsperminut:3,docutil:[10,1,13,2,12],"0x7fa41cb98d50":4,unit:[4,12,3,7],unoffici:13,refer:[11,7],subset:13,found:[10,1,13,2,12],enough:13,graph:13,should:[8,1],some:[13,14],tuesdai:12,bsd:7,replai:14,thread:14,reset_control_command:14,build:7,more:[8,12,13,11],much:14,json:[0,1,11,5,10,2,12,13],redirect:10,number:[4,13,7],interact:8,main:[8,7],mail:7,unpars:2,span:[10,1,13,2,12],doc:7,receiv:[8,14,2,11,13],translat:[10,1,2,7,6,13],"0x7fa41cb98bd0":4,control:[8,0,1,7],start:[8,4,13,14],index:7,seventh:4,input_fil:1,datasourc:14,vehicl:[0,1,3,4,7,8,11,12,14],attribut:[4,11],detail:[14,7],sure:7,core:11,mac:7,util:[4,5,9,7],output:[10,12],style:0,work:11,driver:4,determin:4,mai:[8,13],won:8,specifi:[10,1,2,6,13,14],addit:[1,2,7],mani:10,mar:4,map:[4,10],booleanmeasur:4,higher:7,queu:11,backend:7,compound:4,draw:13,functin:11,can:[0,1,11,6,7,8,10,2,12,13],over:13,side:11,calcul:13,larg:12,kilometersperhour:3,rang:[4,13,9],numericmeasur:4,issu:7,birth:9,sudo:7,linux:7,eighth:4,spread:9,instanc:[8,4,0],fourth:4,gear_lever_posit:4,overview:[10,1,13,2,12],max:9,physic:0,liter:[10,1,13,2,12],deseri:5,brakepedalstatu:4,possibl:[10,1,2,12,13,14],github:7,ttyusb0:[10,1,2,6,13,14],ttyusb1:[13,2],mutual:[6,10,1,13,2],execpt:4,hardwar:14,buttonev:4,default_product_id:14,pip:7,adapt:[10,1,2,6,13,14],mixin:[0,9],brew:7,eventedmeasur:4,repositori:7,filename_date_format:11,chunk:12,gap:12,sort:12,until:14,line:[10,1,2,7,6,12,13],advanc:8,ubuntu:7,tracedatasourc:14,weird:0,peek:11,call:[8,4,14,11],like:[14,7],accept:[8,4,0,12],uploadersink:11,notifi:[8,11],comput:8,repres:8,earth:10,total:13,dashboard:[13,7],appear:13,averag:13,test:[14,7],die:14,vendor_id:[10,1,2,6,13,14],type:[8,4,0,13,11],meter:[4,3],trip:12,must:[10,1,4,7,0,11],process:14,"0x1bc4":[6,10,1,13,2],arbitrarili:12,dump:[2,7],button_ev:4,rough:13,messag:[0,1,11,5,8,2,13,14],bool:[4,11],newlin:[1,14],base:[0,1,11,4,6,10,2,12,13,14],tracefil:[6,10,1,13,2],wide:13,zero:8,usbcontrollermixin:0,ahead:11,reset:[0,1],interfac:[0,1,11,4,6,7,8,10,2,13,14],initi:[1,14],pass:[8,14],revers:4,inherit:14,percentag:3,scalar:[4,3],access:8,third:4,overrid:14,kilomet:3,enginespe:4,faster:14,command:[0,1,6,7,8,10,2,12,13],stream:[10,2,11],headlamp_statu:4,plai:[13,2],event:[4,0],longitudinalacceler:4,stdout:[10,2],just:[4,14],site:7,basic:[10,1,7,2,12,13],controllererror:0,minut:12,charact:[0,14],invalid:13,expect:[4,0],pleas:7,tupl:11,http:[14,11,7],otherwis:[4,14],via:[10,1,11,6,7,2,12,13,14],connect:[0,1,6,7,8,10,2,13,14],common:[10,1,2,11,6,13],add:[8,11],write_raw:0,soon:14,been:[8,11],segment:12,program:13,mark:14,particular:2,either:[8,7],custom:[13,2],run:[4,1,14,11,7],three:1,count:13,happen:7,fuelconsum:4,homebrew:7,onli:[14,10,13,2],quit:14,name_from_class:4,quick:[10,1,13,2,12],"import":10,kwarg:[8,4,14,11],deal:8,sinc:13,altern:7,xvfz:7,entir:12,drive:4,than:[8,14,13,2],fuel_level:4,default_baudr:14,none:[8,4,14],relatinoship:0,argument:[10,1,11,4,7,2,12,13],frequenc:13,recommend:7,option:[10,1,6,4,7,8,2,12,13,14],arch:7,out_endpoint:0,applic:[8,4,11,7],accessori:4,convert:10,timestamp:12,lognitudinal_acceler:4,instead:[4,12,13,2],real:[10,13,2],correct:4,from_dict:4,outupt:10,group:12,certian:11,join:7,memori:12,port:[10,1,2,7,6,13,14],turn_signal_statu:[4,1],entri:8,amount:13,raw:[8,10,0,2],noth:8,summari:13,tracker:7,two:12,corrupt:2,readthedoc:7,point:[8,4],odomet:4,measur:[8,4,3,11,7],add_sink:8,intend:7,our:7,cadenc:14,low:[4,7],android:[14,7],"0x7fa41cb9b210":4,vehicle_spe:4,fine_odometer_since_restart:4,which:[8,10,12,14],ford:[10,1,2,7,6,13],googl:10,upload:11,demarc:12,save:10,gearlevelposit:4,firmwar:1,make:13,besid:8,also:[13,7],usb:[10,1,6,7,0,2,13,14],compani:[10,1,2,7,6,13],datasourceerror:14,bug:7,pars:14,unregist:11,dai:12,latest:[8,7],fifth:4,inclus:9,asynchron:11,bluetooth:14,document:[11,7],engine_spe:4,state:4,preferr:7,write_byt:0,path:[10,1,2,6,13,14],setup:7,develop:7,door_statu:4,per:13,measurementnotifiersink:11,fast:14,"0x7fa41cb98fd0":4,keyword:7,product_id:14,usag:7,cannot:14,simultan:13,have:[8,4,14,11,7],get:[8,7],"try":4,"0x7fa41cb9b190":4,file:[10,1,2,11,6,12,13,14],time:[9,10,13,2,12],numer:[4,9],dev:[10,1,2,6,13,14],undef:4,openxc:[0,1,11,3,4,5,6,7,8,9,10,2,12,13,14],simpl:13,deg:4},objnames:{"0":["std","option","option"],"1":["py","module","Python module"],"2":["py","attribute","Python attribute"],"3":["py","function","Python function"],"4":["py","classmethod","Python class method"],"5":["py","class","Python class"],"6":["py","exception","Python exception"]},filenames:["api/controllers","tools/control","tools/dump","api/units","api/measurements","api/formats","_shared/common_cmdoptions","index","api/vehicle","api/utils","tools/gps","api/sinks","tools/tracesplit","tools/dashboard","api/sources"]})