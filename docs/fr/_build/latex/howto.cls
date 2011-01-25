%
% howto.cls for Sphinx
%

\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{howto}[2008/10/18 Document class (Sphinx HOWTO)]

% Pass all given class options to the parent class.
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[twoside]{article}

% Set some sane defaults for section numbering depth and TOC depth.  You can
% reset these counters in your preamble.
%
\setcounter{secnumdepth}{2}

% Change the title page to look a bit better, and fit in with the fncychap
% ``Bjarne'' style a bit better.
%
\renewcommand{\maketitle}{
  \rule{\textwidth}{1pt}
  \ifsphinxpdfoutput
    \begingroup
    % These \defs are required to deal with multi-line authors; it
    % changes \\ to ', ' (comma-space), making it pass muster for
    % generating document info in the PDF file.
    \def\\{, }
    \def\and{and }
    \pdfinfo{
      /Author (\@author)
      /Title (\@title)
    }
    \endgroup
  \fi
  \begin{flushright}
    \sphinxlogo%
    {\rm\Huge\py@HeaderFamily \@title} \par
    {\em\large\py@HeaderFamily \py@release\releaseinfo} \par
    \vspace{25pt}
    {\Large\py@HeaderFamily
      \begin{tabular}[t]{c}
        \@author
      \end{tabular}} \par
    \vspace{25pt}
    \@date \par
    \py@authoraddress \par
  \end{flushright}
  \@thanks
  \setcounter{footnote}{0}
  \let\thanks\relax\let\maketitle\relax
  %\gdef\@thanks{}\gdef\@author{}\gdef\@title{}
}

\let\py@OldTableofcontents=\tableofcontents
\renewcommand{\tableofcontents}{
  \begingroup
    \parskip = 0mm
    \py@OldTableofcontents
  \endgroup
  \rule{\textwidth}{1pt}
  \vspace{12pt}
}  

\@ifundefined{fancyhf}{
  \pagestyle{plain}}{
  \pagestyle{normal}}		% start this way; change for
\pagenumbering{arabic}		% ToC & chapters

\thispagestyle{empty}
