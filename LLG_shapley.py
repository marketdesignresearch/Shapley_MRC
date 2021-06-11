import sympy, itertools, functools

LOCAL_BIDDER_1, LOCAL_BIDDER_2, GLOBAL_BIDDER = sympy.symbols('A B G', positive=True)



def V_weak_locals(coal):
    # assume
    # b_1 < b_g
    # b_2 < b_g
    # b_1 + b_2 > b_g
    
    if coal[0] and coal[1]:
        # locals win over global
        return LOCAL_BIDDER_1 + LOCAL_BIDDER_2
    elif coal[2]:
        # global wins over local
        return GLOBAL_BIDDER
    else:
        # at most one local is active, this covers all 3 remaining cases
        return LOCAL_BIDDER_1 * coal[0] + LOCAL_BIDDER_2 * coal[1]


def V_strong_local_1(coal):
    # assume
    # b_1 > b_g
    # b_2 < b_g
    
    if coal[0]:
        # bidder 1 is active, she always wins
        return LOCAL_BIDDER_1 + LOCAL_BIDDER_2 * coal[1]
    elif coal[2]:
        # global always wins over bidder 2
        return GLOBAL_BIDDER
    else:
        # bidder 2 is the only one potentially left
        return LOCAL_BIDDER_2 * coal[1]


def V_strong_local_2(coal):
    # assume
    # b_1 < b_g
    # b_2 > b_g
    
    if coal[1]:
        # bidder 2 is active, she always wins
        return LOCAL_BIDDER_2 + LOCAL_BIDDER_1 * coal[0]
    elif coal[2]:
        # global always wins over bidder 1
        return GLOBAL_BIDDER
    else:
        # bidder 1 is the only one potentially left
        return LOCAL_BIDDER_1 * coal[0]


def V_strong_locals(coal):
    # assume
    # b_1 > b_g
    # b_2 > b_g
    
    if not (coal[0] or coal[1]):
        # none of the locals is active, global wins if present
        return GLOBAL_BIDDER * coal[2]
    else:
        # at least one local is active, so they always win
        return LOCAL_BIDDER_1 * coal[0] + LOCAL_BIDDER_2 * coal[1]
    


def factorial(i):
    return functools.reduce(int.__mul__, range(1, i+1), 1)




def sub_coalitions(N, i):
    # iterator for all coalitions of bidders.
    # Returned in pairs of coalitions that contain or don't contain bidder i
    N = (1,2,3)
    lowerfacet = [(0,) if j==i else (0, 1) for j in N]
    upperfacet = [(1,) if j==i else (0, 1) for j in N]
    yield from zip(itertools.product(*lowerfacet), itertools.product(*upperfacet))


def shapley_payoff(i, V, with_seller=False):
    N = (1,2,3)
    n = 3
    res = 0
    #print("payoffs:")
    for coal, coal_i in sub_coalitions(N, i):
        size= sum(coal)
        
        
        if with_seller:
            # Since only coalitions with the seller have any value, we can implicitly assume that the seller is present.
            # However, the weights are different because n and size have to be replaced by (n+1) and (size+1), respectively.
            weight = sympy.Integer(factorial(size+1) * factorial(n-size-1)) / factorial(n+1)
        else:
            weight = sympy.Integer(factorial(size) * factorial(n-size-1)) / factorial(n)
        
        
        #print(f"    {coal},   {weight},   ({V(coal_i)})  -  ({V(coal)})  =  {V(coal_i)  -  V(coal)}")
        res += weight * (V(coal_i) - V(coal))
    return res


def shapley_payment(i, V):
    value = [LOCAL_BIDDER_1, LOCAL_BIDDER_2, GLOBAL_BIDDER][i-1] 
    return value - shapley_payoff(i, V)



def make_shapley_table_latex(with_seller=False):
    cases = [
        (r"locals\\weak", V_weak_locals), 
        (r"local 1\\strong", V_strong_local_1), 
        (r"local 2\\strong", V_strong_local_2), 
        (r"locals\\strong", V_strong_locals),
    ]
    
    
    #payment rules are hardcoded:
        # fp
        # VCG
        # shapley payment & payoff, without seller
        # shapley payment & payoff, with seller
    
     
    rules = [
        r"\multirow{2}{1cm}{First\\Price}", 
        r"\multirow{2}{0.6cm}{VCG}", 
        r"\multirow{2}{3.1cm}{Shapley payment\\w/o seller}", 
        r"\multirow{2}{2.8cm}{Shapley payoff\\w/o seller}", 
        r"\multirow{2}{3.1cm}{Shapley payment\\w/ seller}", 
        r"\multirow{2}{2.8cm}{Shapley payoff\\w/ seller}", 
    ]
    
    
    result1 = []
    result1.append( f"\\begin{{tabular}}{{|l|l|{len(rules)*'l|'}}}" )
    
    # first line
    result1.append( r"\hline" )
    result1.append( r"\multicolumn{2}{|l|}{\bf Case} & \bf " + r"& \bf ".join(rules) + r"\\" )
    result1.append( r"\multicolumn{2}{|l|}{} &" + "&" * (len(rules) - 1) + r"\\" )
    result1.append( f"\hhline{{:=:=:{'=:' * len(rules)}}}" )
    
    result2 = result1[:]
    
    
    
    
    for name, valuation_func in cases:
        # compute payments and payoffs
        payoffs_wo = [
            shapley_payoff(1, valuation_func, with_seller=False),
            shapley_payoff(2, valuation_func, with_seller=False)
        ]
        
        
        payments_wo = (LOCAL_BIDDER_1 - payoffs_wo[0], LOCAL_BIDDER_2 - payoffs_wo[1])
        
        
        payoffs_w = [
            shapley_payoff(1, valuation_func, with_seller=True),
            shapley_payoff(2, valuation_func, with_seller=True),
        ]
        
        payments_w = (LOCAL_BIDDER_1 - payoffs_w[0], LOCAL_BIDDER_2 - payoffs_w[1])
        
        
        fp = [ LOCAL_BIDDER_1, LOCAL_BIDDER_2 ]
        vcg = [ 
            GLOBAL_BIDDER - LOCAL_BIDDER_2 if valuation_func in (V_weak_locals, V_strong_local_1) else sympy.Integer(0),
            GLOBAL_BIDDER - LOCAL_BIDDER_1 if valuation_func in (V_weak_locals, V_strong_local_2) else sympy.Integer(0),
        ]
        
        # This will be the first two rows of data
        expressions = [
            fp,
            vcg,
            payments_wo,
            payoffs_wo,
            payments_w,
            payoffs_w,
        ]
        
        # now the derivatives (always wrt A)
        derivatives = [
            (sympy.diff(e[0], LOCAL_BIDDER_1), sympy.diff(e[1], LOCAL_BIDDER_1))
            for e in expressions
        ]
        
        # finally, the sensitivity
        sensitivity = [
            e[0] - e[1] for e in derivatives
        ]
        
        
        # 2nd data table: when is core proj independent of IR constraints?
        EPS = sympy.symbols(r'\varepsilon', positive=True)
        EPS_1, EPS_2 = sympy.symbols(r'\varepsilon_1 \varepsilon_2', positive=True)
        indep_IR_1 = [
            (e[0] >= e[1] - GLOBAL_BIDDER + 2* LOCAL_BIDDER_1)
            #.subs(LOCAL_BIDDER_2, GLOBAL_BIDDER - LOCAL_BIDDER_1 + EPS)
            .simplify()
            for e in expressions
        ]
        # brute-force experimentation shows that these substitutions allow maximum simplification of the equations
        if valuation_func in (V_strong_local_2, V_strong_locals):
            indep_IR_1 = [
                e.subs(LOCAL_BIDDER_2, GLOBAL_BIDDER + EPS_2).simplify()
                for e in indep_IR_1
            ]
        
        if valuation_func in (V_strong_local_1, V_strong_locals):
            indep_IR_1 = [
                e.subs(GLOBAL_BIDDER, LOCAL_BIDDER_1 - EPS_1).simplify()
                for e in indep_IR_1
            ]
        
        
        # Now, do the same with IR constraint of the other bidder
        indep_IR_2 = [
            (e[0] <= e[1] + GLOBAL_BIDDER - 2* LOCAL_BIDDER_2)
            .simplify()
            for e in expressions
        ]
        if valuation_func in (V_strong_local_2, V_strong_locals):
            indep_IR_2 = [
                e.subs(LOCAL_BIDDER_2, GLOBAL_BIDDER + EPS_2).simplify()
                for e in indep_IR_2
            ]
        
        if valuation_func in (V_strong_local_1, V_strong_locals):
            indep_IR_2 = [
                e.subs(GLOBAL_BIDDER, LOCAL_BIDDER_1 - EPS_1).simplify()
                for e in indep_IR_2
            ]
        
        def stringify_formula(f):
            #return sympy.latex(f, mode="inline", mul_symbol="dot")
            return r"$ \displaystyle " + sympy.latex(f, mul_symbol="dot") + "$"
            
        def stringify_pair(pair):
            f,g = pair
            return r"$ \displaystyle \left( " + sympy.latex(f, mul_symbol="dot") + ", " + sympy.latex(g, mul_symbol="dot") + r"\right) $"
        
        
        result1.append(f"\multirow{{4}}{{1.2cm}}{{\small {name}}} & \small $p_1$ & \small " 
                      + r"& \small ".join(stringify_formula(e[0]) for e in expressions) 
                      + r"\\[5pt]" )
        result1.append( f"& \small $p_2$ & \small " 
                      + "& \small ".join(stringify_formula(e[1]) for e in expressions) 
                      + r"\\[5pt]" )
        
        result1.append(r"& \small $\frac{\partial}{\partial A}$ & \small " 
                      + r"& \small ".join(stringify_pair(e) for e in derivatives)
                      + r"\\[5pt]" )
        result1.append( f"& \small $sens_1(p(b))$ & \small " 
                      + r"& \small ".join(stringify_formula(e) for e in sensitivity) 
                      + r"\\[5pt]" )
        result1.append( r"\hline" )
        
        
        result2.append( f"\multirow{{2}}{{1.2cm}}{{\small {name}}} & \small IR bidder 1 & \small " 
                      + r"& \small ".join(stringify_formula(e) for e in indep_IR_1) 
                      + r"\\[5pt]" )
        result2.append( f"& \small IR bidder 2 & \small " 
                      + r"& \small ".join(stringify_formula(e) for e in indep_IR_2) 
                      + r"\\[5pt]" )
        result2.append( r"\hline" )
        
        

        
    result1.append(r"\end{tabular}")
    result2.append(r"\end{tabular}")
    
    return("\n".join(result1), "\n".join(result2))
    #return( "\n".join(result1))



tables = make_shapley_table_latex()

with open("LLG_shapley_table1.tex", "w") as fd:
    fd.write(tables[0])
    
with open("LLG_shapley_table2.tex", "w") as fd:
    fd.write(tables[1])

