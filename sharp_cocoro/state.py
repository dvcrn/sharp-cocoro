class State8:
    def __init__(self, state: str = '0' * 160):
        self.state = state

    @property
    def temperature(self) -> float:
        t = f"{self.state[52]}{self.state[53]}"
        return int(t, 16) / 2

    @temperature.setter
    def temperature(self, t: float) -> None:
        s = list(self.state)
        hex_temp = hex(int(t * 2))[2:].zfill(2)
        s[52] = hex_temp[0]
        s[53] = hex_temp[1]

        s[6] = '2'

        hex_temp2 = hex(int((t + 16) * 2))[2:].zfill(2)
        s[0] = hex_temp2[0]
        s[1] = hex_temp2[1]

        self.state = ''.join(s)

    @property
    def fan_direction(self) -> int:
        # Read fan direction from positions 96-97 as a 2-digit number
        return int(self.state[96:98])

    @fan_direction.setter
    def fan_direction(self, fan_state: int) -> None:
        # For command states, we don't restore temperature
        # The command template should remain intact
        s = list(self.state)
        
        # Position 0-1: hex(0xC1 + fan_state) as 2-char hex string
        hex_value = f"{0xC1 + fan_state:02x}"
        s[0] = hex_value[0]
        s[1] = hex_value[1]
        
        # Position 96-97: fan_state as 2-digit decimal with leading zero
        decimal_value = f"{fan_state:02d}"
        s[96] = decimal_value[0]
        s[97] = decimal_value[1]
        
        self.state = ''.join(s)
