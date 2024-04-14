import sympy


# 长径-短径
def getLongbyShort(x_in):
    temp = 0.0
    # coefficients
    a = -2.2427707646190047E+00
    b = 2.0123090794235963E+00
    c = -1.1279402674379879E-02
    temp += a + b * x_in + c * (x_in ** 2)
    return temp


# 长径-功率、时间
def longAboutPowerTime(x_in, y_in):
    # x_in为功率 y_in为时间
    temp = 0.0
    # coefficients
    a = -4.1720244793823023E+00
    b = 3.0705500236155683E-03
    c = -1.7223938155026002E+00
    d = 6.0929967948700472E-03
    f = 3.3774400633753060E-01
    g = -3.6493055555523578E-05
    h = -1.1258089595194254E-02
    i = 8.3995429688280165E-02
    j = -3.7995192307700086E-04
    k = -2.2043585229135389E-03
    temp = a
    temp += b * x_in
    temp += c * y_in
    temp += d * (x_in ** 2)
    temp += f * (y_in ** 2)
    temp += g * (x_in ** 3)
    temp += h * (y_in ** 3)
    temp += i * x_in * y_in
    temp += j * (x_in ** 2) * y_in
    temp += k * x_in * (y_in ** 2.0)
    return temp


# 短径-功率、时间
def shortAboutPowerTime(x_in, y_in):
    # x_in为功率 y_in为时间
    temp = 0.0
    # coefficients
    a = -1.3763240274081772E+01
    b = 5.3408810569949194E-01
    c = 1.7447732314451758E+00
    d = -5.3256410256519856E-03
    f = -2.8470722932661274E-01
    g = 1.8680555555539158E-05
    h = 1.2610085547205977E-02
    i = 5.1702896292057876E-02
    j = -1.9663461538446669E-04
    k = -1.0050321032682823E-03
    temp = a
    temp += b * x_in
    temp += c * y_in
    temp += d * (x_in ** 2)
    temp += f * (y_in ** 2)
    temp += g * (x_in ** 3)
    temp += h * (y_in ** 3)
    temp += i * x_in * y_in
    temp += j * (x_in ** 2) * y_in
    temp += k * x_in * (y_in ** 2)
    return temp


def solve_equation(short_diameter):
    long_diameter = getLongbyShort(short_diameter)
    print("short_diameter = {} (mm), long_diameter = {} (mm)"
          .format(short_diameter, long_diameter))
    x = sympy.Symbol('x', real=True)
    y = sympy.Symbol('y', real=True)
    shortEq = shortAboutPowerTime(x, y) - short_diameter
    longEq = longAboutPowerTime(x, y) - long_diameter
    eqs = [shortEq, longEq]
    solved_value = sympy.nsolve(eqs, [x, y], [50, 5], verify=False)
    return long_diameter, solved_value
    # print(sympy.latex(solved_value))
    # print("power = {} (W), time = {} (mins)".format(solved_value[0],
    #                                                 solved_value[1]))

def solve_equation_v2(long_diameter, short_diameter):
    print("short_diameter = {} (mm), long_diameter = {} (mm)"
          .format(short_diameter, long_diameter))
    x = sympy.Symbol('x', real=True)
    y = sympy.Symbol('y', real=True)
    shortEq = shortAboutPowerTime(x, y) - short_diameter
    longEq = longAboutPowerTime(x, y) - long_diameter
    eqs = [shortEq, longEq]
    solved_value = sympy.nsolve(eqs, [x, y], [50, 5], verify=False)
    return solved_value

if __name__ == '__main__':
    # input short diameter
    short_diameter = 40.3945678899
    solve_equation(short_diameter)
    # # # output
    # short_diameter = 17.2 (mm), long_diameter = 28.51144193095297 (mm)
    # power = 46.1440570358360 (W), time = 9.04991903125099 (mins)
