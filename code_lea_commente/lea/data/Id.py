import datetime
import calendar

class Id :
    """
    :param index: Sert à reconnaitre deux Data crée le même jour
    :type index: int
    :param typ: Quelle est le type d'expérimentation faite
    :type typ: str
    :param who: Personne ayant pris le Data
    :type who: str
    :param date: Date quand l'expérience a été réalisé
    :type date: str
    :param heure: variable plus utilisée
    """
    def __init__(self, **kwargs):
        self.gen(**kwargs)

    def gen(self,index=1,typ="Non spécifié", who="SPerrard", date="", heure=""):
        self.index=index
        self.typ=typ
        self.who=who
        if date=="" : #Si la date n'est pas rentrée, mets la date du jour
            self.date = datetime.datetime.now().strftime('%Y%m%d')
        else :
            self.check_date(date)
            self.date=date
        if heure=="": #Si l'heure n'est pas rentrée, mets l'heure du jour
            self.heure = datetime.datetime.now().strftime('%H%M')
        else :
            self.check_heure(heure)
            self.heure=heure

            #Vérifie si la date est correcte, format : année, mois, jour
    def check_date(self, date):
        if len(date)!=8 :
            raise Exception('La date n\'est pas au bon format.\n \
            La date entrée est : {}'.format(date))
        if(int(date[0:4])<2000):
            print("Vielles données")
        if(int(date[4:6])>12 or int(date[4:6])<1):
            raise Exception('La date ne contient pas un mois correct.\n \
            Le mois entré est : {}'.format(date[4:6]))
        if(int(date[6:8]) > calendar.monthrange(int(date[0:4]), int(date[4:6]))[1]):
            raise Exception('La date ne contient pas un jour correct.\n \
            Le jour entré est : {}'.format(date[6:8]))

        #Vérifie si l'heure est correcte, format : heure minute
    def check_heure(self, heure):
        if len(heure)!=4 :
            raise Exception('L\'heure n\'est pas au bon format.\n \
            L\'heure entrée est : {}'.format(heure))
        if(int(heure[0:2])>24):
            raise Exception('L\'heure ne contient pas une heure correcte.\n \
            L\'heure entré est : {}'.format(heure[0:2]))
        if(int(heure[2:4])>59):
            raise Exception('L\'heure ne contient pas des minutes correctes.\n \
            Les minutes entrés sont : {}'.format(heure[2:4]))


    def get_name(self):
        """
        :return: Le nom de l'objet, ici "Id"

        .. warning:: Fonction nécessaire à toute les classes lors qu'on veut les convertir en hdf5

        """
        return "Id"
