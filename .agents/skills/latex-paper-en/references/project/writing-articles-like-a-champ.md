# Writing rules – Written via e-mails by Ido and Thomas, Edited by Yaniv

Source: `_agents_outputs/_agents_dump/writing articles like a champ.docx`

Project-local companion reference for `latex-paper-en`.

Converted from the Word document into Markdown for readability. Wording is preserved; only structure and formatting were changed.

## Intro: Color method

Don't be scared by all the colors :)

my color scheme is the following:

yellow means comments.

green means text I suggest to add

red means text I suggest to remove

add the figures at the end. put captions too.

----

when you modify things, use the same color scheme. Whatever you accept you just leave white. But whatever you add mark in green and whatever you remove in red. Use some color for responding to my comments.

These marks are important, so we keep all the comments and not lose track of different questions and comments (e.g., don't delete a comment without answering to it - instead leave it there and ask about it in another comment if you're not sure).

Normally, in steady state, the amount of colors is significantly smaller than this :) but it always starts like this!

You can answer to different points by other comments with your comments color – either say why you keep it one way, or why you agree and change it to another way. I'm deleting them whenever I think they're done and I saw that you responded to them. If I don't see your response to a comment then I assume you missed that comment – then I leave it there. If I don't agree with the changes or they are not enough, then I leave the comment too and write something more.

You should do the same thing exactly: remove a comment that I responded to if you have no other question. Also remove everything that I marked red (unless you want it back and then mark it in green). And remove the coloring from everything I marked green (unless you want to remove it and then mark it red). If you forget to remove the color from something I marked in green I'll assume that you added it because I don't remember what I did J

## How to write

- Scientific reports are most commonly written in present tense – go through the text to check this point and modify (this is one of the tests for text that professional writers sometimes suggest).
- we need to think about the pitch –So we need to write the intro in a way that explains why the above claim is interesting and why it is worth solving
- the next two paragraphs are your “here we”. Normally it is better to start with the “in this work” or “here we show”. Only after it you should put the explanation of the intuition paragraph. Why flip the order? Because people may not know what is new and what was done before. The “we suppose that” paragraph makes it look like these ideas are already well known and are not part of our novel claims. Putting it after the “here we” make it clearer that these are new ideas
- with the graphs. Better to present a little theory and get to results, and then more theory and more results, instead of all the theory and then all the results
- discussion – several paragraphs here. Mention how this generalizes to other systems. Then say that the most exciting is that… Finally say that this can potentially be used to… adding some bombastic conclusion
- The work can benefit a lot from an "English teacher" going through it to improve the writing
- saying easy to produce always annoys experimentalists
- entangled is a risky word
- Backslash is never used in prose. If any slash, it should be forward-slash (which should generally be avoided as well).
- Fermi is a person—not a thing! Capitalize. (comment on writing fermi level)
- Write in the active voice: ‘Figure 2a-d reveals a large frequency shift…’. The passive voice is boring. (comment on “In Figure 2a-d a large frequency shift is revealed”)
- When you try to write the sentence in a descriptive way (as it is currently), it often becomes quite boring and—what’s worse—unnecessarily lengthy. Instead, write it as something doing something. ‘X shows Y’ or ‘Y does Z (see X)’ not ‘In X we show Y’.
- Don’t write ‘will be’, which is weak and uncertain, when a shorter, more direct and assertive option is available: ‘is’. Even better, write: ‘absorption is not possible/impossible/forbidden’. (comment to “there will be no possible absorption”)
- professional writers suggest to put a paragraph like this one “in section X we do Y and in section Z we do W” only for your own organization. Then remove it in the end because the reader doesn’t care. So I try to use it to be useful as a selling piece: by making it into part of the here we paragraph in a sense… pronouncing the findings and not just listing them J
- When starting a sentence, abbreviations must be written in full. (Equation 2 and not Eq. 2)
- Introduction: I don't think that a long introduction is necessarily bad, as long as we manage three things 1 simple to follow the logic 2 clear at every point "why are you telling me this" 3 showing strong motivation and importance. Ask yourself these three questions at every paragraph after you modify things.
- Results: Each paragraph has a single topic and that's good, then try to report the findings with simpler sentences inside each paragraph, and try to optimize the order of the content in it.
- If doing a complete rewrite it's better to mark in red and put a new one in green so it's easier to compare that all the content is there (but I know it's easier said than done… 😊)]
- In equations: I think that the period should be on the left side of the number.

## Appearance

- note that I changed the text alignment to “justify”[cntrl+J] – this looks nicer.
- change all the font to be the same all over the text (potentially having a different font for figure captions.
- Note that the equation number should be on the right side, and aligned to the right. The best way to do that is the following (note the alignment and the use of tabs to push the equation back to the center). Do that in all the rest of the equations.
- note that we need to keep the consistency of how we refer to figures: either “figure X” or “Fig.X”].
- need to keep consistent how we refer to the equations: so far it was without the “eq”.
- Subscripts on mathematical symbols should be in roman font (i.e. not italic) if the subscripts are descriptive in nature; e.g. if the subscript ‘pl’ is short for ‘plasmon’, it should be roman. If a subscript refers to another variable, it should be italic. This way, you don’t run into trouble e.g. with differentiating between ‘i’ denoting a vector’s index and an abbreviation of ‘initial’. I’ve fixed this throughout.
- You should punctuate your equations as if they were part of the text. See e.g. the amusing and always instructive columns by Mermin (Rule 3 of What’s wrong with these equations?).
- A space is needed between a number and its unit – moreover, the unit is never in italic (to distinguish clearly between variables and unit systems). I.e. 300nm should be 300 nm.
- Equations, in most journals, are preceded by ‘Eq.’: that is, ‘see (2)’ should be ‘see Eq. (2)’. If we need to start a sentence with ‘Eq. (2)’ we should write ‘Equation (2)’ (same for e.g. Fig.)
- Don’t make large swaths of text italic: it lowers readability (fixed in captions).
- Don’t write text in the equation environment: this results in an awkward mixing of fonts and typefaces and ruins spacing.
- Subfigures are presently referenced in an inconsistent manner, e.g. occasionally as Fig. 1ab, occasionally as Fig. 1(a,b) etc.

## Figures

- Remember that people often will read a paper by only looking at the figures initially: if one needs to refer back to the text N times to do so, one stops reading the paper. Accordingly, figures should be self-explanatory as far as possible (without becoming overly cluttered). Also remember that the figure caption is similarly less attractive to read than the figure itself (i.e. the figure should be as readable as possible without the caption).
- make sure you edit them in powerpoint slides and just copy the cropped images to here.
- Q:“what should a add in matlab except grid and ticks for axis?” A: The less you add in Matlab the happier you'll be later. Try to add everything possible in powerpoint
- Add captions below the figures.
- Pedantic: avoid “pure” (e.g. RGB [0,0,253] for blue) colors; use “broken”/”flat” colors; see e.g. http://www.flatuicolorpicker.com/
- It is better to have some spacing between your subfigures (even if they share axis, a small space is preferable).
- Don’t use italic text in figures unless used for mathematical variables.
- Direct-label your lines as far as possible, and try to match color of labels and lines unless it results in something jarring.
- Don’t put the axis ticks inside the figures: they are always outside the axis.
- Don’t use gridlines, they are almost never useful (a corollary of this is never to use lines between columns/rows in tables, except for rows separating data from labels). It is simply noise and justified only for situations where graphs need to be read with often and with substantial accuracy (say, if you work in a production facility or as a laboratory technician; we fortunately don’t).
- Figures must have meaningful labels (e.g. the x-axis in Fig. 2 is only given a unit not a variable nor a name!).: especially on the axes—a bit of human-readable text to accompany equations is useful.
- Figures should preferably be vector graphics: bitmap is pain.
- Sans serif fonts are better than serif fonts in figures.
- Caption need to start with a title for every figure
- Don’t capitalize every word of a label/annotation. This is solely for titles.
- Comment for a children paper:" The units in (a) are italic L. The y-label unit of ‘transition/sec’ could more clearly simply be Hz. If it were a rate of apples falling per second and we were writing a popular article, we might write apples/sec – but for scientific papers, it’s preferable to have ‘Apple drop rate (Hz)’. Here, we can simply have ‘Transition rate \Gamma_{pl} (Hz)’"
- Finally, the various font-sizes (this is a general issue for the figures) vary without any real consistency. E.g the legend here is much larger than all other text. The annotations, on the other hand, are too small (though it is good that they are slightly smaller than all other text). Figures should be consistent.
- Generally, I try to make the font in the figure at the same size as the caption’s font. Otherwise it’s too small. We won’t change that now. Instead I tried to increase the size of the figure by going over the margins (no one will complain)
- Supp figures : We’ll put the figure in parenthesis and not as the subject of the sentence because it makes it look like we’re building on the supp too much
- Need a more informative caption title.

## Code

- If you have things that run for very long, then a useful advice is to get used to saving the output data in a file and having a separate function that creates the figure from that data file. This way you can make small modifications (zoom in, change colors, change scales,...) without rerunning the code.

## References

- In the abstract you cannot put citations, but then in the introduction you should definitely have them.
- You can leave empty brackets for now [], and then fill them later
- First references should be from good journals\Einstein\ big names in the field
- Remember to cite all the papers that we discussed in regard to this work (best way is to copy them into the bottom of the text and mark which ones are cited and which ones are not yet cited so we don’t forget anything important – search your email for that).
- we need to check that we cite whoever we recommend in the cover letter
- To add references - a useful trick: place the author name and year like in the example: [Jablan2009]. Then in the reference list, instead of numbering them, put the name and year instead of the number. Only right before submission you change to numbers. Otherwise you’ll have to renumber every time we change some order of things or add a ref in the intro, and it’s a headache J
- Q: I am having trouble with the citations of the most basic topics. A: Typically a review paper or the first paper or both. Check what is highly cited in google scholar + what is in a good journal.

## Abstract

we need to start with a few sentences of putting us in a broader context (which you did) and presenting a gap (a missing piece of knowledge / an unanswered question / a desired outcome / a known application).

Then we start with "here we" did it.

The gap is very important and has to be super strongly motivated. This is the first thing that people care about.

Another point of advice: don't try to make it short right away.

It's true that in some journals the size is limited, but even there we first write something long and then we shrink it. The cutting process is normally improving the quality gradually.

So start with putting the best sentences and claims without worrying about the length too much. For example give the nonlocality and the spectral shift separate sentences (I think that makes them more clear as two points of strength)

Then the final sentence is an outlook of a sort. Something that can be a bit wild and shows the potential implications/applications that will come out from the direction of research that we started.

Fonts – (for real experts)

While the "optimal" font (see [1]) of course depends on circumstance and case of usage, I myself am quite fond of two particular typefaces. Depending on whether serif (serious stuff; papers, chapters etc) or sans serif (less serious/friendly; posters, slides, and figure labels) I like, respectively, MinionPro and MyriadPro which are two commercial (i.e. expensive, unless bundled with software) typefaces from Adobe.

To avoid paying, as always, one can simply, say, borrow: http://fontsup.com/. For convenience, I've attached (bottom link) a selection of typefaces I like as a .zip archive. To install them, simply press enter on all the files (at once), and Windows should take care of the rest (MyriadPro and MinionPro are included).

[1] Supposedly, one is supposed to actually call this a typeface; then a font is a particular subset of a typeface - e.g. bold - and a typeface is then the collection/family of fonts. Truely an example of an unnecessary distinction.

PS. If you ever wondered what typeface Nature journals use for their figures (probably you have better things to wonder about; but somehow, I have found myself wondering) - it is one called Whitney (in the, there you have it, 'Book' font). It is nice compared to other sans serif's for labels because it is very compact yet legible!

https://drive.google.com/open?id=0Bw3EGeBSpfA_SVlrNFhMQk9ZSFE3

## Supplementary Information

- cant’s say expression for the equations. it’s either expression for the processes or develop the equations implemented in the paper.
- redefine acronyms since the document is different than the main text.  better to define everything here and not assume the main text is used unless you point explicitly to the main text. generally we try to make this part stand alone
- ' '  I reordered the definitions for a few reasons. wanted the longest one with the parenthesis to be last since it's easiest to read .since it takes more space between the lines and this way it's the least ugly in making the space weird
- typically, present tense
- Equation alignments - note the alignment is normally to the left in the upper part and right in the lower par

## Submission

- Always submit only a PDF. Word is too risky because it may look different in different computers and we don't want the referees to reduce points for what is a technical computer problem.
- It advised to only use Ido’s account to submit from. This can be the difference between the editors letting a paper through to referees, and them being slightly more positive.

## Response to reviewers

- Thank everybody all the time:

Open with: " We thank the reviewers for their careful evaluation and helpful remarks. We have modified the manuscript accordingly and our responses to their comments are given below. "

After opening notes of a referee: "We thank the reviewer for the positive review."

After a comment:" We thank the referee for this recommendation."

- After every comment add an explanation and finish with showing explicitly what has changed : "Additions and modifications:"
- It could be easy to add the sentence:" Note to all of the reviewers: new additions to the manuscript are signified by light blue font."
- There is only one file for all referees, so we can send him\her there :" We direct the reviewer to the opening notes of reviewer #2, that elaborate on this issue."
- Call them he\she:" We thank the reviewer for this comment, he\she is correct."
- If the reviewer made the spelling mistake, consider fixing it for them in this case.
- My preference is that one should generally make every citation of a paper in a reply little a hyperlink (to a DOI link): referees don’t want to spend time looking up papers, and we should indicate with every opportunity that we value their time (… and hence them).
- This is condescending towards the referee—let’s avoid that. As a response to “We also provide the following plot for the referee’s use”.
- Every paper that the reviewers comment about must be cited in the paper. Even if it is not related at all – just to make them happy.
- Attempt to answer this question in a weakly phrased manner means that most of this paragraph is borderline science speak/meaningless jargon.
- It would be better to say that we emphasize something rather than minimize something. E.g. it would be better to say  ‘Accordingly, we have sought to emphasize the essential role played by weak coupling in the revised manuscript. Below, we indicate two relevant places where such additional clarifications have been made:’  (then you would, of course, have to make such changes to the manuscript)
- Better to just try to explicate an approach like the one he suggests that works (i.e. do our best to make him happy!)
- Normally we try to just use one term – referee or reviewer. Not that crucial.
- “Made the effort” sounds a bit like we didn’t try to do it before -> made special efforts, that professional.
- What do we add to the manuscript about it? Every comment deserves at least a sentence. If the change is so small (or only in the supp) that it looks embarrassing, then we write here just: “We revised the discussion towards the end of the manuscript to bring some more info about these interesting prospects” or “Our supplementary materials now contains more information about the above discussion” or something like that.
- Strong coupling is not a term he uses. So if your point is that part of his question is related to that, we need to first say that it is related.
- Give the files a careful read to look for the simple mistakes. (spacer length vs thickness)
- This sounds a bit insulting. “Added a sentence” after he wrote 2 paragraphs about it.
- when we feel that the change is too small, we copy the entire paragraph and not just the single sentence. Since there are other small changes in the sentences surrounding the new sentence, then we can color all of it in blue
- It’s a good idea to point the referee to similar comments by others, especially that the others are more positive than him/her J
- Not to answer to a referee that we cited what he is talking about :" Our middle finger in his face. “We cited other Lamb shift papers but not yours!”
- Important to write it in a way that it’s clear that it is a new change following his comment, and not something that we had already. So the tense matter:" We now emphasize"
- If we don’t agree: We fully appreciate the referee’s comment. Indeed,... However…
- Format: Reviewers: Bald, line spacing 1.5; Article: line spacing 2, changes in blue; Response: line spacing 1.15.

## Writing checklist from English book:

- Use a spell checker, but they do not catch all mistakes. Some suggest looking at your paper backwards.
- Watch wordiness:
- Shorten all "which, that, who," prepositional phrases, and any redundant info (it, there):
- Use short words and concise terms:
- Have à possess
- Enough à sufficient
- Use à utilize
- Due to the fact that à because
- The vast majority of à most
- During the time that à when
- Use verbs instead of nouns.
- Take into consideration à consider
- Use strong content verbs instead of have, be, go, get, make, do, etc. whenever possible.
- Flow:
- Sentences should not be longer than 40 words. Use two sentences for more than 40 words. In general, sentences should have 1-3 ideas in 1-3 lines.
- Watch flow. Each sentence/idea should be connected to that before/after. The same is true for paragraphs. Each paragraph should connect to the one before/after.
- Make sure you have divided your work into paragraphs and that they are properly indented (TAB).
- Watch confusables:  varying, various; effect, affect; continuous, continual, etc.
- Verbs:
- Use active voice. It's clearer and more concise than passive.
- Use first person when possible (it saves the use of passive)- ex. We.
- Double check tenses- remember which tenses are typical of each section of the article.
- Watch sentence structure:
- Avoid dangling participles.
- "After incubating at 30 degrees C, we examined the petri plates."
- Watch parallelism in lists and complex sentences with and, but, etc.
- Check your punctuation:
- Especially commas
- Watch proper capitalization
- Nouns:
- Watch the "s" in the noun compounds- they should be dropped.
- Hard fields articles à hard field articles
- Check your articles- a,an (=for singular countable nouns only) and the.
- Check non-count/count nouns you are unsure of.
- Remember these are non-counts:
- Work//Research//Knowledge//equipment//evidence
- Moves

Use the moves when you begin writing a section of your article

## removes for writing a paper

The editor’s point of view: https://www.youtube.com/watch?v=UVhINwCrUzc

## TODO

- Ref conventions – by journal, consistency, see previous papers.
- Mendelayevgoogle scholar/manual review
- Elaborate on fluent text.
- Cite from site