import pandas as pd
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import costs as costs
from scipy.interpolate import splrep, splev
from pathlib import Path

show = True

base_dir = str(Path().resolve())

colors = ['bo', 'ro', 'go', 'mo', 'co', 'yo', 'ko']
colorsl = ['b', 'r', 'g', 'm', 'c', 'y', 'k']


class Predictor2():
    def __init__(self, df, ConfTable, Profiles, Mixtures, MixtureProfiles, costs):
        self.df = df
        self.ConfTable = ConfTable
        self.Profiles = Profiles
        self.Mixtures = Mixtures
        self.MixtureProfiles = MixtureProfiles
        self.costs = costs
        self.x = []
        self.ConfMeasuredData = {}
        self.ConfPredictedData = {}
        self.MixID=0##################################

    def MAR(self, val, bspl_Rate, bspl_KO):
        x = np.linspace(0, 400, 40)
        rates = splev(x, bspl_Rate)
        KOs = splev(x, bspl_KO)
        mar = rates[0]
        for j in range(len(x)):
            if ((KOs[j] < val) and (mar < rates[j])):
                mar = rates[j]
            # print " eval MAR["+str(val)+"%] ko:"+str(ko[j])+" mar:"+str(mar)
        return mar

    def plot_MAR(self, profile, type):
        plt.clf()  ##################################################   altrimenti mi sovrappone i grafici
        length = len(self.ConfTable)
        x = np.linspace(0, 400, 40)
        mar5 = []
        if (type == 'measured'):
            data = self.ConfMeasuredData
        elif (type == 'predicted'):
            data = self.ConfPredictedData
        else:
            print('which type of MAR is the one for ' + type)

        for i in range(length):
            print
            "Plot " + type + " MAR for " + self.ConfTable[i] + " on" + profile
            mar5.append(self.MAR(5, data[self.ConfTable[i]][3], data[self.ConfTable[i]][0]))
        x_axis = np.arange(0, length)
        bar = plt.barh(x_axis, mar5, color='k')
        plt.yticks(x_axis + 0.5, self.ConfTable, rotation='horizontal');
        plt.xlabel('rate')
        for idx, rect in enumerate(bar):
            width = rect.get_width()
            cost = round(self.costs.costFromString(self.ConfTable[idx]), 4)
            scost = str(cost) + ' $/h'
            plt.text(width + 10, rect.get_y() + rect.get_height() / 2., round(mar5[idx], 2), ha='center', va='bottom',
                     rotation=0)
            plt.text(0.5 * width, rect.get_y() + rect.get_height() / 2., scost, ha='center', va='bottom', rotation=0,
                     color='white', fontweight='bold', fontsize=14)
        plt.title(profile + ' - MAR - KO max:5%')
        plt.savefig(base_dir + '/output/plot_' + profile.strip() + '_' + type + 'MAR.png', bbox_inches='tight', dpi=150)
        #plt.show() ##############ho aggiunto questo metodo per mostrare il grafico
        #plt.clf()

        img = BytesIO()
        plt.savefig(img)
        img.seek(0)
        return img

    def plotError(self, x, measured, predicted, i, Conf):
        m = np.array(measured)
        p = np.array(predicted)
        erra = np.absolute(m - p)
        err = 100 * np.divide(erra, m)
        plt.plot(x, err, colorsl[i], label=Conf)

    def plot(self, x, bsplm, i, Conf):

        plt.plot(x, splev(x, bsplm), colors[i], label=Conf)
        plt.plot(x, splev(x, bsplm), colorsl[i])

        img = BytesIO()
        plt.savefig(img)
        img.seek(0)
        return img

    def plotAll(self, index, typePlot):
        plt.legend(loc="upper left")
        plt.xlabel('Cuser')
        plt.ylabel(index)
        plt.title(index + ' ' + typePlot)
        plt.savefig(base_dir + '/output/plot_' + index + '_' + typePlot + '.png', bbox_inches='tight', dpi=500)

        img = BytesIO()
        plt.savefig(img)
        img.seek(0)
        return img


    # KO Mixture Prediction
    # SUM(mi*KOpi(cuser))
    def predictKO(self, x, mix, bsplKOs):
        awKO = mix[0] * splev(x, bsplKOs[0])
        ewKO = mix[1] * splev(x, bsplKOs[1])
        swKO = mix[2] * splev(x, bsplKOs[2])
        rwKO = mix[3] * splev(x, bsplKOs[3])
        KOarray = np.array([awKO, ewKO, swKO, rwKO])
        pMixKO = np.sum(KOarray, axis=0)
        bspl_pMixKO = splrep(x, pMixKO)
        return [KOarray, pMixKO, bspl_pMixKO]

    # Rate prediction with KO weights
    def predictRate(self, x, mix, KOdata, bspl_Rates):
        wrates = [np.divide(KOdata[0][0], KOdata[1]), np.divide(KOdata[0][1], KOdata[1]),
                  np.divide(KOdata[0][2], KOdata[1]), np.divide(KOdata[0][3], KOdata[1])]
        Rates = [splev(x, bspl_Rates[0]), splev(x, bspl_Rates[1]), splev(x, bspl_Rates[2]), splev(x, bspl_Rates[3])]
        weightedRates = [np.multiply(wrates[0], Rates[0]), np.multiply(wrates[1], Rates[1]),
                         np.multiply(wrates[2], Rates[2]), np.multiply(wrates[3], Rates[3])]
        pMixRate = np.sum(weightedRates, axis=0)
        bspl_pMixRate = splrep(x, pMixRate)
        return [pMixRate, bspl_pMixRate]

    # RT Prediction (simple weighted mean)
    def predictRT(self, x, mix, bspl_RTs):
        RTs = [splev(x, bspl_RTs[0]), splev(x, bspl_RTs[1]), splev(x, bspl_RTs[2]), splev(x, bspl_RTs[3])]
        RT = [mix[0] * RTs[0], mix[1] * RTs[1], mix[2] * RTs[2], mix[3] * RTs[3]]
        pMixRT = np.sum(RT, axis=0)
        bspl_pMixRT = splrep(x, pMixRT)
        return [pMixRT, bspl_pMixRT]

    # RT*Rate prediction
    def predictRTrate(self, cum, mix, bspl_RTs, bspl_Rates):
        aRTrate = mix[0] * np.multiply(splev(cum, bspl_Rates[0]), splev(cum, bspl_RTs[0]))
        eRTrate = mix[1] * np.multiply(splev(cum, bspl_Rates[1]), splev(cum, bspl_RTs[1]))
        sRTrate = mix[2] * np.multiply(splev(cum, bspl_Rates[2]), splev(cum, bspl_RTs[2]))
        rRTrate = mix[3] * np.multiply(splev(cum, bspl_Rates[3]), splev(cum, bspl_RTs[3]))

        RTrate = [aRTrate, eRTrate, sRTrate, rRTrate]
        pMixRTrate = np.sum(RTrate, axis=0)
        bspl_pMixRTrate = splrep(cum, pMixRTrate)
        return [pMixRTrate, bspl_pMixRTrate]

    def InterpolateProfile(self, Conf, Profile):
        DF1 = self.df.loc[(self.df['Conf'] == Conf) & (self.df['profile'] == Profile)]  # author
        cuser = DF1['Cuser']
        Rate = DF1['rate']
        KO = DF1['%KO']
        RT = DF1['RT']
        bspl_KO = splrep(cuser, KO)
        bspl_Rate = splrep(cuser, Rate)
        bspl_RT = splrep(cuser, RT)
        return [cuser, bspl_KO, bspl_RT, bspl_Rate]

    def predict(self, MixID):
        length = len(self.ConfTable)
        self.MixID=MixID##############################
        for i in range(length):
            print('Evaluating ' + self.ConfTable[i])
            mix = self.Mixtures[MixID]
            author = self.InterpolateProfile(self.ConfTable[i], self.Profiles[0])
            editor = self.InterpolateProfile(self.ConfTable[i], self.Profiles[1])
            shopmanager = self.InterpolateProfile(self.ConfTable[i], self.Profiles[2])
            reader = self.InterpolateProfile(self.ConfTable[i], self.Profiles[3])

            mixture = self.InterpolateProfile(self.ConfTable[i], self.MixtureProfiles[MixID])

            # Order Interpolate Functions by Parameter
            bspl_KOs = [author[1], editor[1], shopmanager[1], reader[1]]
            bspl_RTs = [author[2], editor[2], shopmanager[2], reader[2]]
            bspl_Rates = [author[3], editor[3], shopmanager[3], reader[3]]

            # Interpolate Mixture measurements
            cum = mixture[0]
            bspl_mMixKO = mixture[1]
            bspl_mMixRT = mixture[2]
            bspl_mMixRate = mixture[3]
            mMixRTrate = np.multiply(splev(cum, bspl_mMixRT), splev(cum, bspl_mMixRate))
            bspl_mMixRTrate = splrep(cum, mMixRTrate)

            # KO Prediction
            KOdata = self.predictKO(cum, mix, bspl_KOs)
            bspl_pMixKO = KOdata[2]
            pMixKO = KOdata[1]

            # Rate Prediction with KO weights
            Ratedata = self.predictRate(cum, mix, KOdata, bspl_Rates)
            bspl_pMixRate = Ratedata[1]
            pMixRate = Ratedata[0]

            # RT Prediction
            RTdata = self.predictRT(cum, mix, bspl_RTs)
            pMixRT = RTdata[0]
            bspl_pMixRT = RTdata[1]

            RTratedata = self.predictRTrate(cum, mix, bspl_RTs, bspl_Rates)
            pMixRTrate = RTratedata[0]
            bspl_pMixRTrate = RTratedata[1]

            self.x = cum
            self.ConfMeasuredData[self.ConfTable[i]] = [bspl_mMixKO, bspl_mMixRTrate, bspl_mMixRT, bspl_mMixRate]
            self.ConfPredictedData[self.ConfTable[i]] = [bspl_pMixKO, bspl_pMixRTrate, bspl_pMixRT, bspl_pMixRate]
            # self.plotPrediction(cum,'RTRate', mMixARTrate,pMixARTrate, bspl_mMixARTrate, bspl_pMixARTrate)
            # self.plotError(cum,'RTRate', mMixARTrate,pMixARTrate, bspl_mMixARTrate, bspl_pMixARTrate)

    def plotCTRL(self, index, typePlot):
        print('Plotting ' + typePlot + ' of ' + index)
        plt.clf()  ##################################################   altrimenti mi sovrappone i grafici
        length = len(self.ConfTable)
        cum = self.x
        for i in range(length):
            if (index == 'KO'):
                bsplm = self.ConfMeasuredData[self.ConfTable[i]][0]
                bsplp = self.ConfPredictedData[self.ConfTable[i]][0]
            elif (index == 'Rate'):
                bsplm = self.ConfMeasuredData[self.ConfTable[i]][3]
                bsplp = self.ConfPredictedData[self.ConfTable[i]][3]
            elif (index == 'RT'):
                bsplm = self.ConfMeasuredData[self.ConfTable[i]][2]
                bsplp = self.ConfPredictedData[self.ConfTable[i]][2]
            elif (index == 'RTrate'):
                bsplm = self.ConfMeasuredData[self.ConfTable[i]][1]
                bsplp = self.ConfPredictedData[self.ConfTable[i]][1]
            else:
                print('Unkownn index')

            mpoints = splev(cum, bsplm)
            ppoints = splev(cum, bsplp)

            if (typePlot == 'measured'):
                self.plot(cum, bsplm, i, self.ConfTable[i])
            elif (typePlot == 'predicted'):
                self.plot(cum, bsplp, i, self.ConfTable[i])
            elif (typePlot == 'error'):
                self.plotError(cum, mpoints, ppoints, i, self.ConfTable[i])

            else:
                print('Unkownn plot')

        self.plotAll(index, typePlot)

        img = BytesIO()
        plt.savefig(img)
        img.seek(0)
        return img
