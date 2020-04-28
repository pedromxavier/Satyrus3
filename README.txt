===========
Satyrus III
===========

Introduction
------------


Example
-------

::
    #prec : 33;
    #dir : "C:/Users/Pedro/Desktop";
    #eps : 1E-6;
    #alpha : 1;

    #load : "file.sat"; % "file.sj"


    %{ ------------------------ }
     * Satyrus III Code Example
     *
     *
     { ------------------------ }%


    m = 5;
    n = 3;

    dist[n][n] = { % Distances Array Definition
        (1,1) : 1,
        (n,n) : 1
    };

    x[m][n]; % Solution Array Declaration

    y[m] = {(1) : 1, (2) : 0, (3) : +4, (4) : 2, (5) : -1};

    (int) A[0]: % Integrity Constraint at level 0

    @ {i = [1:5]}
    $ {j = [1:5]}
    @ {k = [1:5]}

    c[i][j] -> x[i][k] & y[j][k];

    (int) B[1]: % Integrity Constraint at level 1

    @ {i = [1:5]}
    @ {j = [1:5]}
    $ {k = [1:5]}

    c[i][j] | (x[i][k] -> y[j][k]);

    (opt) C: % Optimality Constraint  (level 0 as default)

    $ {i = [1:5]}
    $ {k = [1:5]}

    c[i][k] -> y[i][k];

JSON Result
-----------

::
{
    "dir": "C:/Users/Pedro/Desktop",
    "eps": 0.000001,
    "alpha": 1,
    "prec": 33,
       
    "int": [
        [(  "A", 
            [forall(i, 1, 5), exists(j, 1, 5), forall(k, 1, 5)],
            ('|',
                ('[]',
                    ('[]', u, i),
                    j),
                ('->',
                    ('[]',
                        ('[]', x, i),
                        k),
                    ('[]',
                        ('[]', y, j),
                        k)))
          )],
          
        [( "B",
            [forall(i, 1, 5), forall(j, 1, 5), exists(k, 1, 5)],
            
        )]
    ]
}
