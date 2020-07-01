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

%%

\endinput