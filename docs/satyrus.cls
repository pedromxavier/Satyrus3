\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{satyrus}[30/06/2020 Satyrus]

%% Article options
\DeclareOption{12pt}{
  \PassOptionsToClass{\CurrentOption}{memoir}
}
\DeclareOption{openany}{
  \PassOptionsToClass{\CurrentOption}{memoir}
}
\DeclareOption{twoside}{
  \PassOptionsToClass{\CurrentOption}{memoir}
}

%% Fallback
\DeclareOption*{
  \ClassWarning{bookstyle}{Unknown option '\CurrentOption'}
}

%% Execute default options
\ExecuteOptions{12pt}

%% Process given options
\ProcessOptions\relax

%% Load base
\LoadClass[a4paper]{memoir}

%% Load additional packages and commands.
\RequirePackage{xcolor}
\RequirePackage[utf8]{inputenc}
\RequirePackage{float}
\RequirePackage{graphicx}
\RequirePackage{xspace}
\RequirePackage{listings}

%% Additional TeX/LaTeX code...

\setlength{\parskip}{\baselineskip}%
\setlength{\parindent}{20pt}%

\nouppercaseheads
\makepagestyle{mystyle} 
\setlength{\headwidth}{\dimexpr\textwidth+\marginparsep+\marginparwidth\relax}
\makerunningwidth{mystyle}{\headwidth}
\makeevenfoot{mystyle}{}{\thepage}{} 
\makeoddfoot{mystyle}{}{\thepage}{} 
\makeatletter
\makepsmarks{mystyle}{%
  \createmark{chapter}{left}{shownumber}{\@chapapp\ }{.\ }}
\makeatother

\makepagestyle{plain}
\makerunningwidth{plain}{\headwidth}
\makeevenfoot{plain}{}{}{}
\makeoddfoot{plain}{}{}{}

\pagestyle{mystyle}

\renewcommand{\cftchapterdotsep}{\cftdotsep}
\renewcommand\contentsname{}

%% Names
\definecolor{codecolor}{rgb}{0.0, 0.0, 0.6}
\definecolor{stringcolor}{rgb}{0.0, 0.6, 0.0}
\definecolor{emphcolor}{rgb}{0.6, 0.0, 0.6}
\definecolor{commentcolor}{rgb}{0.6, 0.6, 0.6}

\newcommand{\keywordstyle}{%%
	\itshape\bfseries\color{codecolor}
}

\newcommand{\emphstyle}{%%
	\itshape\bfseries\color{emphcolor}
}

\newcommand{\stringstyle}{%%
	\itshape\bfseries\color{stringcolor}
}

\newcommand{\commentstyle}{%%
	\itshape\bfseries\color{commentcolor}
}

\newcommand{\code}[1]{%%
	{\keywordstyle #1}%%
}

\newcommand{\type}[1]{%%
	{\emphstyle #1}%%
}


%% LISTINGS

\lstdefinestyle{bashstyle}
{
	numberblanklines=true,
	tabsize=4,
	gobble=4,
	frame=single,
	stringstyle={\stringstyle},
	keywordstyle={\keywordstyle},
	morekeywords={%  
		def, seja, enquanto, para, cada, em, se, retorna, continua, e, ou%
	},
	emphstyle={\emphstyle},
	emph={%
	},
	commentstyle={\commentstyle},
	numbers=left,
	stepnumber=1,
	showstringspaces=false,
	basicstyle=\ttfamily,
	mathescape=false,
	breaklines=true,
	breakatwhitespace=false,
	extendedchars=true,
	inputencoding=utf8,
	xleftmargin=1cm,
	morecomment=[l]{//},
	morecomment=[s]{/*}{*/},
	morestring=[b]",
	literate=
	{ã}{{\~a}}1                         {õ}{{\~o}}1 
	{Ã}{{\~A}}1                         {Õ}{{\~O}}1 
	{á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1
	{Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1
	{à}{{\`a}}1 {è}{{\`e}}1 {ì}{{\`i}}1 {ò}{{\`o}}1 {ù}{{\`u}}1
	{À}{{\`A}}1 {È}{{\'E}}1 {Ì}{{\`I}}1 {Ò}{{\`O}}1 {Ù}{{\`U}}1
	{ä}{{\"a}}1 {ë}{{\"e}}1 {ï}{{\"i}}1 {ö}{{\"o}}1 {ü}{{\"u}}1
	{Ä}{{\"A}}1 {Ë}{{\"E}}1 {Ï}{{\"I}}1 {Ö}{{\"O}}1 {Ü}{{\"U}}1
	{â}{{\^a}}1 {ê}{{\^e}}1 {î}{{\^i}}1 {ô}{{\^o}}1 {û}{{\^u}}1
	{Â}{{\^A}}1 {Ê}{{\^E}}1 {Î}{{\^I}}1 {Ô}{{\^O}}1 {Û}{{\^U}}1
	{œ}{{\oe}}1 {Œ}{{\OE}}1 {æ}{{\ae}}1 {Æ}{{\AE}}1 {ß}{{\ss}}1
	{ç}{{\c c}}1 {Ç}{{\c C}}1 {ø}{{\o}}1 {å}{{\r a}}1 {Å}{{\r A}}1
	{€}{{\EUR}}1 {£}{{\pounds}}1
	%%
	{~}{{{\raisebox{0.5ex}{\texttildelow}}}}1
	,
}

\lstdefinestyle{satishstyle}
{
	numberblanklines=true,
	tabsize=4,
	gobble=4,
	frame=single,
	stringstyle={\stringstyle},
	keywordstyle={\keywordstyle},
	morekeywords={%  
		def, seja, enquanto, para, cada, em, se, retorna, continua, e, ou%
	},
	emphstyle={\emphstyle},
	emph={%
	},
	commentstyle={\commentstyle},
	numbers=left,
	stepnumber=1,
	showstringspaces=false,
	basicstyle=\ttfamily,
	mathescape=true,
	breaklines=true,
	breakatwhitespace=false,
	extendedchars=true,
	inputencoding=utf8,
	xleftmargin=1.5cm,
	morecomment=[l]{//},
	morecomment=[s]{/*}{*/},
	morestring=[b]",
	literate=
	{ã}{{\~a}}1                         {õ}{{\~o}}1 
	{Ã}{{\~A}}1                         {Õ}{{\~O}}1 
	{á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1
	{Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1
	{à}{{\`a}}1 {è}{{\`e}}1 {ì}{{\`i}}1 {ò}{{\`o}}1 {ù}{{\`u}}1
	{À}{{\`A}}1 {È}{{\'E}}1 {Ì}{{\`I}}1 {Ò}{{\`O}}1 {Ù}{{\`U}}1
	{ä}{{\"a}}1 {ë}{{\"e}}1 {ï}{{\"i}}1 {ö}{{\"o}}1 {ü}{{\"u}}1
	{Ä}{{\"A}}1 {Ë}{{\"E}}1 {Ï}{{\"I}}1 {Ö}{{\"O}}1 {Ü}{{\"U}}1
	{â}{{\^a}}1 {ê}{{\^e}}1 {î}{{\^i}}1 {ô}{{\^o}}1 {û}{{\^u}}1
	{Â}{{\^A}}1 {Ê}{{\^E}}1 {Î}{{\^I}}1 {Ô}{{\^O}}1 {Û}{{\^U}}1
	{œ}{{\oe}}1 {Œ}{{\OE}}1 {æ}{{\ae}}1 {Æ}{{\AE}}1 {ß}{{\ss}}1
	{ç}{{\c c}}1 {Ç}{{\c C}}1 {ø}{{\o}}1 {å}{{\r a}}1 {Å}{{\r A}}1
	{€}{{\EUR}}1 {£}{{\pounds}}1
	%%
	{~}{{{\raisebox{0.5ex}{\texttildelow}}}}1
	{<-}{{{$\leftarrow$}}}1
	{->}{{{$\rightarrow$}}}1
	{<->}{{{$\longleftrightarrow$}}}1
	,
}

\lstnewenvironment{satish}{%%
	\lstset{style=satishstyle}
	\vspace{5pt}
}{%%
}

\lstnewenvironment{bash}{%%
	\lstset{style=bashstyle}
	\vspace{5pt}
}{%%
}

\lstnewenvironment{shell}{%%
	\lstset{style=bashstyle}
	\vspace{5pt}
}{%%
}

\endinput