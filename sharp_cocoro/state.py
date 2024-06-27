class State8:
    def __init__(self, state: str = '0' * 160):
        self.state = state

    @property
    def temperature(self) -> float:
        t = f"{self.state[52]}{self.state[53]}"
        return int(t, 16) / 2

    @temperature.setter
    def temperature(self, t: float):
        s = list(self.state)
        hex_temp = hex(int(t * 2))[2:].zfill(2)
        s[52] = hex_temp[0]
        s[53] = hex_temp[1]

        s[6] = '2'

        hex_temp2 = hex(int((t + 16) * 2))[2:].zfill(2)
        s[0] = hex_temp2[0]
        s[1] = hex_temp2[1]

        self.state = ''.join(s)