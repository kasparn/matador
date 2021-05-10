import numpy as np
import sys
#define class for actions
class GameAction:
   
    #takes to which field (index) in moveVal and with what probability in prob
    def __init__( self, field_end, prob ):
        self.field_end = field_end
        self.prob = prob

    #static function that finds the probability of landing on a given field for a given start field
    #  the state of the dice and the general game class instance defining rules 
    @staticmethod
    def findAction( fieldStart, dice, game ):
        #finds the field we end up at right after throwing the dice. Afterwards, we decide what to do from there
        f_end_pos = fieldStart.pos + dice.val()
        #truncate to restart from zero when above the number of fields
        if f_end_pos >= game.noFields:
            f_end_pos = f_end_pos - game.noFields 

        fieldEnd = game.fields[f_end_pos]
        action = []
        #If in prison and the dice are not equal then stay
        #Otherwise, move. In order to model "get out of prison on the third throw regardless",
        #  we employ the probability of hitting two identical dice throws in a row
        #prisonProb gives the probability that we have hit two non-identical dice in a row
        prisonProb = 0
        if fieldStart.type == Field.fieldPrison:
            if dice.dieOneVal != dice.dieTwoVal:
                #action for not moving out - subtract the probability that this is the third throw, i.e. move out regardless
                prisonProb = 5./6. * 5./6.
                action.append( GameAction( game.prisonField, prisonProb ) )
        elif dice.dieOneVal == dice.dieTwoVal:
            #if not in prison but hitting to identical dice
            prisonProb = 1./6. * 1./6. #prob that this is the third time in a row hitting two identical dice
            action.append( GameAction( game.prisonField, prisonProb ) )
        #in this case we will move regardless
        if fieldEnd.type == Field.fieldProperty:
            #landing on a property means you stay there
            action.append( GameAction( f_end_pos, 1.0-prisonProb ) )
        elif fieldEnd.type == Field.fieldGotoPrison:
            #landed on the "goto prison field and will thus have to... go to prison ;)"
            action.append( GameAction( f_end_pos, 1.0 - prisonProb ) )
        elif fieldEnd.type == Field.fieldChance:
            #landed on a question-mark and should return the possible outcomes with their respective probabilities
            action.append( GameAction( game.prisonField, 1/6 - prisonProb ) ) # one in six chance cards are "go straight to prison"
            action.append( GameAction( f_end_pos, 5/6 - prisonProb ) ) #the rest are, for now, "stay"

            
        return action

#defines game class
class Game:
    prisonMaxThrows = 3 #defines the throw number (counted from zero) at which the player has to come out of prison regardless of the dice
    noFields = 40 #defines the number of fields on the plate
    prisonField = 30 #defines which field is the "go to prison field"
    def __init__(self):
        self.fields = []
        #build up the board (start by making property fields only for testing)
        for f in range(Game.noFields):
            if f==30:
                self.fields.append(Field(Field.fieldGotoPrison, 11))    #note that the field "goto prison" is field 30 while the field "in prison" is field 11
            elif f==2 or f==7 or f==17 or f==22 or f==33 or f==36:
                self.fields.append( Field( Field.fieldChance, f+1) )
            else:
                self.fields.append(Field(Field.fieldProperty, f+1))
        

#defines the field class
class Field:
    fieldProperty = 0 #defines the field to be a property
    fieldChance = 1 #defines the field to be a chance field
    fieldPrison = 2 #defines the field to be "in prison"
    fieldGotoPrison = 3 #defines the field "go to prison"
    def __init__( self, type, pos ):
        self.type = type
        self.pos = pos


    def __str__( self ):
        return "Type = {}, pos = {}".format(self.type,self.pos)
#defines the dice class
class Dice:
    def __init__(self, dieOneVal, dieTwoVal):
        self.dieOneVal = dieOneVal
        self.dieTwoVal = dieTwoVal
    
    def prob(self):
        return 1./36.

    def val(self):
        return self.dieOneVal+self.dieTwoVal

    def __str__(self):
        return "Dice: {}, {}".format(self.dieOneVal,self.dieTwoVal)

    @staticmethod
    def combinations():
        combi = [   ]
        for i in range(6):
            for j in range(6):
                combi.append( Dice(i+1,j+1) )
        return combi

g = Game()

k = Dice.combinations()
moveMat = np.zeros(shape=(g.noFields,g.noFields))

#loop over each field
for f in g.fields:
    #loop over each possible dice combination
    for d in Dice.combinations():
        #get the action(s) at this particular throw
        actions = GameAction.findAction( f, d, g )
        #loop over the action(s) - sometimes there is more than possible outcome and each is associated with a probability and they sum to one
        for a in actions:
            #find the start and end fields
            ind_start = f.pos - 1 #Python is index-1 based
            ind_end = a.field_end - 1
            moveMat[ind_start,ind_end] = moveMat[ind_start,ind_end] + a.prob * d.prob() #each possible outcome of the dice is 1/36

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(linewidth=200)
print( moveMat[21,:] )
print( sum(moveMat[21,:]))

m2 = np.matmul( moveMat, moveMat )
m4 = np.matmul( m2, m2 )
m8 = np.matmul( m4, m4 )
m16 = np.matmul( m8, m8 )

print( moveMat[:,29])
print( m16[:,29])