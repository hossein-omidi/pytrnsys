# -*- coding: utf-8 -*-
"""
Created on Thu Aug 08 07:57:08 2013

@author: dcarbone
"""

import os, shutil
import string

class CreateTrnsysDeck():
    
    def __init__(self,_path,_name,_variations):
        
        self.originalName = _name
        self.path = _path
        self.originalDeckName = os.path.join(self.path ,self.originalName +'.dck')
        self.variations = _variations                
        
        print "name:%s path:%s deckName:%s\n" % (self.originalName,self.path,self.originalDeckName)
        
        split = self.originalName.split('-')

        try: #DC : Why do we need a special strucutre of the name? Can we ignore that?
            self.case = split[0]
            self.system = split[1]
            self.building = split[2]
            self.city = split[3] 
        except:
            pass
        
        self.deckOutputs = []
        self.combineAllCases=False
        
        self.createNewOne =True # In principle always on. Otherwise if a dck is found its not created again, and 
        # if we have changed something from the original we will no see the changes if this is set to False.
        # I will erase this if no utility after a while.

    def generateDecks(self):
        """
        This function will generate as many deck cases as the number of variations defined in the confg file.
        The deck are stored in self.path using the variations and the base name to create the individual names
        :return:
        """
        self.myListOfParameterDicts =[]

        if(self.combineAllCases==False):
            for i in range (len(self.variations)):
                
                for j in range(len(self.variations[i])):
                    
                    if(j==0): 
                        # A comprensible name to be used as a tag in the file
                        nameLabelOfVariation = self.variations[i][j]
                    elif(j==1):
                        #the name how it is called inside the deck
                        nameVariationInDeck  = self.variations[i][j]
                    else:
                        valuesOfVariationInFile = self.variations[i][j]
                        
                        #If the name has 00 means 0. because the fileName will suffer from having points as names.
                        if(valuesOfVariationInFile=="00"):
                            valuesOfVariation = "0."+ valuesOfVariationInFile[2:]                                    
                            print "Comma found valueFile=%s valueUsed=%s" % (valuesOfVariationInFile,valuesOfVariation)
                        else:
                            valuesOfVariation = valuesOfVariationInFile
#                            print "Comma NOT found valueFile=%s valueUsed=%s" % (valuesOfVariationInFile,valuesOfVariation)
                        
                        #ToDo : DC To me we shuold not use of this naming structure but just take the name we find and add variaitons at the end

                        nameDeck = "%s-%s%s%s-%s-%s" % (self.case,self.system,nameLabelOfVariation,valuesOfVariationInFile,self.building,self.city)            
                        self.deckOutputs.append(nameDeck)
                        nameDeckCreated = "%s\%s.dck" % (self.path,nameDeck)
                        
    #                    print "DECK GENERATED :%s " % nameDeckCreated
                        
                        if(os.path.isfile(nameDeckCreated)):
                            if(self.createNewOne):
                                os.remove(nameDeckCreated)
                                shutil.copy(self.originalDeckName,nameDeckCreated)                            
                            else:
                                print "File exist, I do not create a new one"                        
                            pass
                        else:                     
                            shutil.copy(self.originalDeckName,nameDeckCreated)    
                        
                        parameterDict = {}
                        parameterDict[nameVariationInDeck]= valuesOfVariation
        
                        print parameterDict                                
                        self.myListOfParameterDicts.append(parameterDict)
        else:
            #For this case we assume they all have the same lenght
        
            nameLabelOfVariation = []
            nameVariationInDeck = []
            
            for nvar in range (len(self.variations)):
                nameLabelOfVariation.append(self.variations[nvar][0])
                nameVariationInDeck.append(self.variations[nvar][1])
            
#            print nameLabelOfVariation
#            print nameVariationInDeck
#            print len(self.variations[0])-2
            #all tags must have the same number of values    

            if(len(self.variations)>0):
                for j in range(2,len(self.variations[0])):

                        variationsLine =""
                        for nvar in range (len(self.variations)):

                            valuesOfVariationInFile = self.variations[nvar][j]

                            # If I write variation = ["","","GFX",...] then I add the name to the deck but no variation is used
                            if(len(self.variations[nvar][0])==0 and len(self.variations[nvar][1])==0):
                                variationsLine = variationsLine + "-%s" % (valuesOfVariationInFile)

                            #If I write variation = ["","useCovered",0,1] then no value is printed
                            elif(len(self.variations[nvar][0])>0):
                                variationsLine = variationsLine + "-%s%s" % (self.variations[nvar][0],valuesOfVariationInFile)

    #                        print "nameLabel:%s values:%s" % (self.variations[nvar][0],valuesOfVariationInFile)

                        try:
                            nameDeck = "%s-%s%s-%s-%s" % (self.case,self.system,variationsLine,self.building,self.city)
                        except:
                            nameDeck = "%s%s" % (self.case,variationsLine)

    #                    print nameDeck

                        self.deckOutputs.append(nameDeck)
                        nameDeckCreated = "%s\%s.dck" % (self.path,nameDeck)

                        #print "DECK GENERATED :%s " % nameDeckCreated

                        if(os.path.isfile(nameDeckCreated)):
                            if(self.createNewOne):
                                os.remove(nameDeckCreated)
                                shutil.copy(self.originalDeckName,nameDeckCreated)
                            else:
                                print "File exist, I do not create a new one"
                            pass
                        else:
                            shutil.copy(self.originalDeckName,nameDeckCreated)

                        parameterDict = {}

                        for nvar in range (len(self.variations)):
                            variationString = "%s" % self.variations[nvar][j]

                            if(variationString[:2]=="00"):
                                valuesOfVariation = "0."+ variationString[2:]
                                print "Comma found valueFile=%s valueUsed=%s" % (variationString,valuesOfVariation)
                            else:
                                valuesOfVariation = variationString
                                print "Comma NOT found valueFile=%s valueUsed=%s" % (variationString,valuesOfVariation)

                            parameterDict[nameVariationInDeck[nvar]]= valuesOfVariation

                        print parameterDict
                        self.myListOfParameterDicts.append(parameterDict)

#            print "myListOfParameterDict"
#            print self.myListOfParameterDicts
            
              
#        print self.deckOutputs
        
        return  self.deckOutputs
               
    def getParameters(self,i):
           
        return self.myListOfParameterDicts[i]
        
#        print  self.myListOfDicts
    
#    def getParameters(self)        
#        return self.deckOutputs



#Missing