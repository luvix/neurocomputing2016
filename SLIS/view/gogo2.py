import controller
from controller import projio
from controller import simagent
import numpy as np
# from model import metrics_CPON as cmetrics


class SimulationCaseController:
    def __init__(self, fold: int):
        self._fold = fold
        self._agentlist = []
        pass

    @property
    def fold(self):
        return self._fold

    def __getitem__(self, item):
        return self._agentlist[item]

    def fit(self, agent: simagent.SimAgent, **kwargs):
        """
        agent을 등록하고, 두가지 case로 입력된 데이터를 받는다.
        case #1: 그냥 data와 target이 입력된 경우
        그냥 data와 target을 입력한다.
        case #2: lc, lt, ec, et가 지정된 경우
        지정해서 입력한다.
        :param agent:
        :param kwargs:
        :return:
        """
        if 'data' in kwargs and 'target' in kwargs:
            """
            case #1: 그냥 data와 target이 입력된 경우
            그냥 data와 target을 입력한다.
           """
            agent.folder.fit(kwargs['data'], kwargs['target'])
        elif 'lc' in kwargs and 'lt' in kwargs and 'ec' in kwargs and 'et' in kwargs:
            """
            case #2: lc, lt, ec, et가 지정된 경우
            지정해서 입력한다.
            """
            lm = agent.folder
            lm.uploadlearn(kwargs['lc'], kwargs['lt'])
            lm.uploadexam(kwargs['ec'], kwargs['et'])
            agent.folder = lm
        else:
            print('뭔 개짓거리?')
            return False
        self._agentlist.append({'agent': agent})
        pass

    def simulate(self, simulatecase: str):
        for agentdict in self._agentlist:
            sa = agentdict['agent']

            if not isinstance(sa, simagent.SimAgent):
                return False

            if 'known' in simulatecase:
                agentdict['result'] = sa.simulate()

            elif 'unknown' in simulatecase:
                agentdict['result'] = sa.simulate_unknown()

            yield agentdict['result']

    @staticmethod
    def factory():
        sa = simagent.SimAgent()
        return sa


if __name__ == "__main__":
    data, target = projio.load('D:/workshop/NIPLAB/leesuk.kim/raw/50[FREQ,PW,dTOA]') # 실제 논문에서 사용한 dataset (tb.1)
    # data, target = projio.load('D:/workshop/NIPLAB/leesuk.kim/raw/50[FREQ,PW,TOA]') # 실제 논문에서 사용한 dataset (tb.2, tb.3)

    sac = SimulationCaseController(fold=10)

    sa = simagent.SimAgent(sac.fold)
    sa.addsim(simagent.clffactory('cpon'))
    sac.fit(sa, data=data, target=target)

    sacgen = sac.simulate('known')
    stats = []
    for res in sacgen:
        agent = res
        stats.append(res[0].statistics)  # 0번째 sim의 statistics

    fsclist = []
    scfdict = {'acc': [], 'f_a': [], 'p_a': [], 'r_a': []}
    for fold in stats:
        for key in fold:
            scfdict[key].append([x for x in fold[key]['fold']])
            # a = 1

    for key in scfdict:
        fclist = scfdict[key]
        cflist = [np.average(x) for x in zip(*fclist)]
        scfdict[key] = cflist
        b = 1

# agent = simagent.SimAgent(fold=10)  # default : 2
    # cpon = simagent.clffactory('cpon')
    # agent.addsim(cpon)
    # lm = agent.folder
    # agent.folder.fit(data, target)
    # lationresult = agent.simulate()
