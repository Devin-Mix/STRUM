# S.T.R.U.M. Tab Specification

Last revised 3/8/2023

---

## Basic syntax

Notes or chords are specified using a six-character sequence. Only six-string guitars are currently supported. Strings which should not be strummed are indicated by a vertical bar character (`|`). Strings which should be strummed and the fret at which to strum them are specified using fret numbers. Open strings are specified using a zero. Rests may be specified using six vertical bars in a row. For example, to specify an E5 chord, the following syntax would be used:

`022|||`

This specifies that the user should play the lowest, second-lowest, and third-lowest strings at frets 0, 2, and 2, respectively, and that the upper three strings should not be played.

Notes or chords are separated by newlines. Each new line is considered to be a new note. All whitespace is stripped from a line unless otherwise specified.

### Note lengths and dots

Note lengths can be specified using hyphens. The addition of one hyphen to note or chord corresponds to halving the length of the note or chord. In sheet music, this would be equivalent to halving the length of a note, e.g. by changing a quarter note to an eighth note. The example above would result in the chord being played for the duration of a whole note. The following example would result in a note with one eighth the length of that above:

`022|||---`

Placing a period after a note or chord will increase the length of the note or chord. The size of this increase depends on the number of periods that precede it. The nth period added to a note increases the length of the note or chord by 1/(2^n) the length specified by its hyphens (or lack thereof). The following examples demonstrate this functionality:

`022|||.`

Without a period, this chord is intended to be played for the length of one whole note. With the period, the chord should be played for an additional length equal to 1/(2^1) = 1/2 that of the whole note. In total, this means that the chord should be played for the length of a whole note plus a half note, or 1.5 whole notes.

`022|||-.`

Without a period, this chord is intended to be played for the length of one half note. With the period, the chord should be played for an additional length equal to 1/(2^1) = 1/2 that of the half note. In total, this means that the chord should be played for the length of a half note plus a quarter note, or 3/4 of a whole note.

`022|||--..`

Without a period, this chord is intended to be played for the length of one quarter note. With the periods, this chord should be played for an additional length equal to (1/(2^1)) + (1/(2^2)) = 3/4 that of the quarter note. In total, this means that the chord should be played for the length of a quarter note plus a 3/16ths note, or 7/16ths of a whole note.

### Ties

In some cases, it may be necessary to extend the length of a note or chord by a non-standard amount. This can be accomplished using ties, which are specified by a plus sign (`+`). A plus sign may be used to add additional length to that specified using hyphens and periods. The resulting note length is the sum of the plus sign-divided lengths, parsed left to right. The following examples outline this behavior.

`022|||-+---`

This example indicates that the chord should be played for the length of one half note plus that of one eighth note, for a grand total of 5/8ths of a whole note.

`022|||+--`

This example indicates that the chord should be played for the length of one whole note plus that of one quarter note, for a grand total of 5/4ths of a whole note.

`022|||+`

This example indicates that the chord should be played for the length of one whole note plus that of one whole note, for a grand total of two whole notes.

`022|||-+---+`

This example indicates that the chord should be played for the length of one half note plus that of one eighth note plus that of one whole note, for a grand total of 13/8ths of a whole note. It is worth noting that the sequence `022|||.+---` could accomplish this as well.

---

## Header syntax

The header precedes the playable content of a tab file. Header content is optional, as the defaults specified below will be used in its absence. Each header option should be present on a separate line. If header content is included, it must be followed by three backslashes (`///`) in order to be parsed correctly.

### Tuning and capo

The default tuning for S.T.R.U.M. is standard tuning, i.e. EADGBe. Alternative tunings may be specified using the command `Tuning=X,X,X,X,X,X`, where each `X` is replaced with a positive or negative integer value. Each value specified corresponds with the tuning of a string, where the lowest and highest strings are the first and last values, respectively. Each increase by 1 in the value for a given string corresponds with an increase in the pitch of that string when played open by one half step (i.e. one fret). For instance, the default standard tuning is equivalent to the tuning specified by `Tuning=0,0,0,0,0,0`, whereas `Tuning=-2,0,0,0,0,0` would correspond to DADGBe due to the low E string's pitch being lowered two half steps.

The tuning command can also be used to specify the usage of a capo. Simply specify the fret on which the capo should be placed. For instance, if the capo is to be placed on fret five of the guitar, `Tuning=5,5,5,5,5,5` would be used.

### Tempo

The tempo of a tab may be specified using the command `BPM=X`, where `X` is replaced with the desired number of quarter note beats per minute. `X` may be an integer or float value.

### Title

The title of a tab may be specified using the command `Title=X`, where `X` is the title.

### Artist

The artist of a tab may be specified using the command `Artist=X`, where `X` is the artist of teh tab's song.