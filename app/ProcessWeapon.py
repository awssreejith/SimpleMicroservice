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
ValueUpdatedSuccess  = 3
InvalidKey           = 4
InvalidType          = 5
NullValue            = 6
DuplicateKey         = 7
BadRequest           = 8
InvalidOrMissingKey  = 9
RecordNotFound       = 10
SUCCESS              = 11
FAIL                 = 12

ID_BIT              = 1
TYPE_BIT            = 2
MANUF_BIT           = 4
COUNTRY_BIT         = 8

@App.route('/weapon',methods=['GET','POST','PUT'])
def ProessRequestForALLWeapon():
    if request.method == 'GET':
        return(jsonify(weaponsDB))
        
    elif request.method == 'POST':
        process = ProcessWeapon()
        jsonObj = process.processPost(request)
        return jsonify(jsonObj)
        
    elif request.method == 'PUT':
        process = ProcessWeapon()
        jsonObj = process.processGet(request)
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
            ## If we reached here.. it means everythig is perfect and we can blindly insert 
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

    def processGet(self, request):
        jsonRequest = request.get_json()
        self.resultMessages.clear()
        ret = self.processGETComplete(jsonRequest)
        if ret == -1:
            self.resultMessages.append(self.createErrorDictionary(BadRequest,0))
        return (self.resultMessages)
 

    def processGETComplete(self,jsonRequest):
        payLoadArray = []
        for idx,key in enumerate(jsonRequest):
            if idx == 0 and key == 'weapons':
                payLoadArray = jsonRequest[key]
                break
            else:
                return -1
        for payload in payLoadArray: ##Normally we should only have one element
            completeBit = self.checkValidKeys(payload)
            if completeBit != (ID_BIT | TYPE_BIT | MANUF_BIT | COUNTRY_BIT):
                self.createErrorDictionary(InvalidOrMissingKey,0)
                return 0
            
            if self.isValidType(payload) == False:
                self.resultMessages.append(self.createErrorDictionary(InvalidType,0))
                return 0
               
            if self.isNotNullValue(payload) == False:
                self.resultMessages.append(self.createErrorDictionary(NullValue,0))
                return 0
               
            if self.isKeyNotExisting(payload) == True: ##If no key..then we shouldn't proceed
                self.resultMessages.append(self.createErrorDictionary(RecordNotFound,0))
                return 0
            ## If we reached here.. it means everythig is perfect and we can blindly update 
            self.updateIntoDB(payload)
            self.resultMessages.append(self.createErrorDictionary(ValueUpdatedSuccess,0))
        return 0
                
                
    def updateIntoDB(self,payload):
        keyFound = False
        for idx,element in enumerate(weaponsDB):
            for key in element:
                if key == 'ID':
                    if element[key] == payload[key]:
                        keyFound = True
                        break ##we got the index to delete
            if keyFound == True:
                break
        ##remove it first
        weaponsDB.pop(idx)
        ##Now add the new values
        weaponsDB.insert(idx,payload)
        return True
 

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
            
        elif errorType == ValueUpdatedSuccess:
            errorMap['Status']  = 'Success'
            errorMap['Message'] = 'Value updated succesfully'
            errorMap['error code'] = 119
            errorMap['serial number'] = index
            return errorMap    

        elif errorType == RecordNotFound:
            errorMap['Status']  = 'Failed'
            errorMap['Message'] = 'Record Not Found'
            errorMap['error code'] = 123
            errorMap['serial number'] = index
            return errorMap              
            
  
        else:
            return {}
            
        

