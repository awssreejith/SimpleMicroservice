#!/bin/bash
from flask import Flask;
from flask import request
from flask import jsonify
from flask import make_response

##Our local DB
weaponsDB=[{"ID"           : "WEAPON_1",
           "TYPE"         : "RIFLE",
           "MANUFACTURER" : "COLT",
           "COUNTRY"      : "USA"
           },
           {"ID"          : "WEAPON_2",
           "TYPE"         : "TANK",
           "MANUFACTURER" : "MERKAVA",
           "COUNTRY"      : "ISRAEL"
           }]
           
           
App = Flask("BANGALORE")  

supportedTypes               = ['RIFLE','TANK','ROCKET','MORTAR']
suppportedKeys               = ['ID','TYPE', 'MANUFACTURER', 'COUNTRY']

ValueInsertedSuccess = 0
ValueDeletedSuccess  = 1
InvalidKey           = 2
InvalidType          = 3
NullValue            = 4
DuplicateKey         = 5
BadRequest           = 6
InvalidOrMissingKey  = 7
SUCCESS              = 8
FAIL                 = 9

ID_BIT              = 1
TYPE_BIT            = 2
MANUF_BIT           = 4
COUNTRY_BIT         = 8

@App.route('/weapon',methods=['GET','POST'])
def ProessRequestForALLWeapon():
    if request.method == 'GET':
        return(jsonify(weaponsDB))
    else:
        process = ProcessWeapon()
        jsonObj = process.processPost(request)
        return jsonify(jsonObj)
        
        
@App.route('/weapon/<string:ID>',methods=['DELETE'])
def ProcessForSpecificWeapon(ID):

    process = ProcessWeapon()
    jsonObj = process.processDelete(ID)

    return jsonify(jsonObj)
        

class ProcessWeapon:
    
    
    def __init__(self):
        self.resultMessages = []
        
    def startService(self):
        App.run(debug=True)
        
      
    def processPost(self,request):
        ## Here we will bifurcate our logic. Client can enter multiple data through JSON
        ## and simple data. If he enters through JSON, then first key should be "weapons" 
        ## and value is an array of dictionary. we first extract this and loop through it.
        jsonPayload = request.get_json()
        self.resultMessages.clear()
        ret = self.processPOSTComplete(jsonPayload)
        
        if ret == -1:
            self.resultMessages.append(self.createErrorDictionary(BadRequest,0))
        return (self.resultMessages)

 

    def processPOSTComplete(self,jsonPayload):
        payloadArray = []
        
        for idx,key in enumerate(jsonPayload):
            if idx == 0 and key == "weapons": ##multiple payload
                payloadArray = jsonPayload[key]
                break
            else:
                return -1
    
        for idx,payload in  enumerate(payloadArray):
        
            completeBit = self.checkValidKeys(payload)
            if completeBit != (ID_BIT + TYPE_BIT + MANUF_BIT + COUNTRY_BIT) :
                self.resultMessages.append(self.createErrorDictionary(InvalidOrMissingKey,idx))
                continue

            if self.isValidType(payload) == False:
                self.resultMessages.append(self.createErrorDictionary(InvalidType,idx))
                continue
               
            if self.isNotNullValue(payload) == False:
                self.resultMessages.append(self.createErrorDictionary(NullValue,idx))
                continue
               
            if self.isKeyNotExisting(payload) == False:
                self.resultMessages.append(self.createErrorDictionary(DuplicateKey,idx))
                continue
            ## If we reached here.. it man everythig is perfect and we can blindly insert 
            self.insertIntoDB(payload)
            self.resultMessages.append(self.createErrorDictionary(ValueInsertedSuccess,idx))
        return 0
        
            
    def processDelete(self,ID):
        ##first check this is is there in weaponsDB
        isFound = False
        isSuccess = False
        for idx,element in enumerate(weaponsDB):
            for key in element:
                if key == 'ID':
                    if element[key] == ID:
                        isFound = True
                        break
            if isFound == True:
                break
        if isFound == True:
            weaponsDB.pop(idx)
            isSuccess = True
        
        if isSuccess == True:
            self.resultMessages.append(self.createErrorDictionary(ValueDeletedSuccess,0))
        else:
            self.resultMessages.append(self.createErrorDictionary(InvalidKeyVlue,0))
        return self.resultMessages
     

    def checkValidKeys(self,payload):
        completeBit = 0
                
        for key in payload:
            if key == 'ID':
                completeBit |= ID_BIT
            elif key == 'TYPE':
                completeBit |= TYPE_BIT
            elif key == 'MANUFACTURER':
                completeBit |= MANUF_BIT 
            elif key == 'COUNTRY':
                completeBit |= COUNTRY_BIT      
            else:
                return 0
        return completeBit
                  
     
    def isValidType(self,payload):
        for key in payload:
            if key == 'TYPE':
                if payload[key] not in supportedTypes:
                    return False
        return True
        
        
    def isNotNullValue(self, payload):
        for key in payload:
            if payload[key] == '':
                return False
        return True
        
    def isKeyNotExisting(self,payload):
        val = ''
        for key in payload:
            if key == 'ID':
                val = payload[key]
                break
        
        ##Check through entire DB for this key
        for element in weaponsDB:
            for key in element:
                if key == 'ID':
                    if element[key] == val:
                        return False
                    else:
                        continue
        return True


    def insertIntoDB(self,jsonPayload):
        weaponDict = {}
        for key in jsonPayload:
            weaponDict[key] = jsonPayload[key]
        weaponsDB.append(weaponDict)
        return True
            
    def createErrorDictionary(self,errorType,index):
        errorMap = {}
        if errorType == ValueInsertedSuccess:
            errorMap['Status']  = 'Success'
            errorMap['Message'] = 'Value inserted succesfully'
            errorMap['error code'] = 0
            errorMap['serial number'] = index
            return errorMap
            
        elif errorType == ValueDeletedSuccess:
            errorMap['Status']  = 'Success'
            errorMap['Message'] = 'Value Deleted succesfully'
            errorMap['error code'] = 0
            errorMap['serial number'] = index
            return errorMap
            
        elif errorType == InvalidKey:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Invalid key provided'
            errorMap['error code'] = 103
            errorMap['serial number'] = index
            return errorMap
            
        elif errorType == InvalidType:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Invalid type provided'
            errorMap['error code'] = 107
            errorMap['serial number'] = index
            return errorMap
 
        elif errorType == NullValue:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Null value provided'
            errorMap['error code'] = 109
            errorMap['serial number'] = index
            return errorMap 
            
        elif errorType == DuplicateKey:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'ID alreay existing'
            errorMap['error code'] = 111
            errorMap['serial number'] = index
            return errorMap

        elif errorType == BadRequest:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Bad JSON Request'
            errorMap['error code'] = 113
            errorMap['serial number'] = index
            return errorMap
            
        elif errorType == InvalidOrMissingKey:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Invalid or missing key'
            errorMap['error code'] = 117
            errorMap['serial number'] = index
            return errorMap
            
  
        else:
            return {}
            
        

