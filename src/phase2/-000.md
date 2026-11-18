# Page −000 — One Script to Rule Them All

```
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ cat > tools/bind_toc.awk << 'END'
# Read the ledgers build.py writes after the PDF is bound.
# One JSON object per line. label and each ghost label bind to that pdf seq.
# stdout is [SYSTEM] only.

function grab_num(line, key,    mark, p, rest, i, c, n) {
    mark = "\"" key "\": "
    p = index(line, mark)
    if (p == 0) return ""
    rest = substr(line, p + length(mark))
    n = ""
    for (i = 1; i <= length(rest); i++) {
        c = substr(rest, i, 1)
        if (c >= "0" && c <= "9") n = n c
        else break
    }
    return n
}

function grab_str(line, key,    mark, p, rest, q) {
    mark = "\"" key "\": \""
    p = index(line, mark)
    if (p == 0) return ""
    rest = substr(line, p + length(mark))
    q = index(rest, "\"")
    if (q == 0) return ""
    return substr(rest, 1, q - 1)
}

function grab_label(line,    s) {
    if (index(line, "\"label\": null")) return "unnumbered"
    s = grab_str(line, "label")
    return s
}

function emit_ghosts(line, seq,    mark, p, rest, inner, n, i, g) {
    mark = "\"ghost_labels\": ["
    p = index(line, mark)
    if (p == 0) return
    rest = substr(line, p + length(mark))
    inner = substr(rest, 1, index(rest, "]") - 1)
    n = split(inner, parts, ",")
    for (i = 1; i <= n; i++) {
        g = parts[i]
        gsub(/[" ]/, "", g)
        if (g != "") {
            printf "[SYSTEM] ghost %s binds pdf %s\n", g, seq
            printf "%s\t%s\tghost\n", g, seq >> out
            ghosts++
        }
    }
}

BEGIN {
    out = "toc_bind.tsv"
    printf "" > out
    print "[SYSTEM] bind open era1_pages.jsonl era2_pages.jsonl"
}

{
    seq = grab_num($0, "seq")
    label = grab_label($0)
    if (seq == "" || label == "") next
    printf "[SYSTEM] %s binds pdf %s\n", label, seq
    printf "%s\t%s\tlabel\n", label, seq >> out
    labels++
    emit_ghosts($0, seq)
}

END {
    close(out)
    printf "[SYSTEM] bind close labels %d ghosts %d wrote toc_bind.tsv\n", labels + 0, ghosts + 0
}
END
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$ awk -f tools/bind_toc.awk era1_pages.jsonl era2_pages.jsonl
[SYSTEM] bind open era1_pages.jsonl era2_pages.jsonl
[SYSTEM] 1 binds pdf 1
[SYSTEM] unnumbered binds pdf 2
[SYSTEM] 1 binds pdf 3
[SYSTEM] 1 binds pdf 4
[SYSTEM] 1 binds pdf 5
[SYSTEM] 1 binds pdf 6
[SYSTEM] 1 binds pdf 7
[SYSTEM] 1 binds pdf 8
[SYSTEM] 1 binds pdf 9
[SYSTEM] 1 binds pdf 10
[SYSTEM] 2 binds pdf 11
[SYSTEM] 3 binds pdf 12
[SYSTEM] 4 binds pdf 13
[SYSTEM] 5 binds pdf 14
[SYSTEM] 6 binds pdf 15
[SYSTEM] 7 binds pdf 16
[SYSTEM] 8 binds pdf 17
[SYSTEM] 9 binds pdf 18
[SYSTEM] 10 binds pdf 19
[SYSTEM] 11 binds pdf 20
[SYSTEM] 12 binds pdf 21
[SYSTEM] 13 binds pdf 22
[SYSTEM] 14 binds pdf 23
[SYSTEM] 15 binds pdf 24
[SYSTEM] 16 binds pdf 25
[SYSTEM] 17 binds pdf 26
[SYSTEM] 18 binds pdf 27
[SYSTEM] 19 binds pdf 28
[SYSTEM] 20 binds pdf 29
[SYSTEM] 21 binds pdf 30
[SYSTEM] 22 binds pdf 31
[SYSTEM] 23 binds pdf 32
[SYSTEM] 24 binds pdf 33
[SYSTEM] 25 binds pdf 34
[SYSTEM] 26 binds pdf 35
[SYSTEM] 27 binds pdf 36
[SYSTEM] 28 binds pdf 37
[SYSTEM] 29 binds pdf 38
[SYSTEM] 30 binds pdf 39
[SYSTEM] 31 binds pdf 40
[SYSTEM] 32 binds pdf 41
[SYSTEM] 33 binds pdf 42
[SYSTEM] 34 binds pdf 43
[SYSTEM] 35 binds pdf 44
[SYSTEM] 36 binds pdf 45
[SYSTEM] 37 binds pdf 46
[SYSTEM] 38 binds pdf 47
[SYSTEM] 39 binds pdf 48
[SYSTEM] 40 binds pdf 49
[SYSTEM] 41 binds pdf 50
[SYSTEM] 42 binds pdf 51
[SYSTEM] 43 binds pdf 52
[SYSTEM] 44 binds pdf 53
[SYSTEM] 45 binds pdf 54
[SYSTEM] 46 binds pdf 55
[SYSTEM] 47 binds pdf 56
[SYSTEM] 48 binds pdf 57
[SYSTEM] 49 binds pdf 58
[SYSTEM] 50 binds pdf 59
[SYSTEM] 51 binds pdf 60
[SYSTEM] 52 binds pdf 61
[SYSTEM] 53 binds pdf 62
[SYSTEM] 54 binds pdf 63
[SYSTEM] 55 binds pdf 64
[SYSTEM] 56 binds pdf 65
[SYSTEM] 57 binds pdf 66
[SYSTEM] 58 binds pdf 67
[SYSTEM] 59 binds pdf 68
[SYSTEM] 60 binds pdf 69
[SYSTEM] 61 binds pdf 70
[SYSTEM] 62 binds pdf 71
[SYSTEM] 63 binds pdf 72
[SYSTEM] 64 binds pdf 73
[SYSTEM] 65 binds pdf 74
[SYSTEM] 66 binds pdf 75
[SYSTEM] 67 binds pdf 76
[SYSTEM] 68 binds pdf 77
[SYSTEM] 69 binds pdf 78
[SYSTEM] 70 binds pdf 79
[SYSTEM] 71 binds pdf 80
[SYSTEM] 72 binds pdf 81
[SYSTEM] 73 binds pdf 82
[SYSTEM] 74 binds pdf 83
[SYSTEM] 75 binds pdf 84
[SYSTEM] 76 binds pdf 85
[SYSTEM] 77 binds pdf 86
[SYSTEM] 78 binds pdf 87
[SYSTEM] 79 binds pdf 88
[SYSTEM] 80 binds pdf 89
[SYSTEM] 81 binds pdf 90
[SYSTEM] 82 binds pdf 91
[SYSTEM] 83 binds pdf 92
[SYSTEM] unnumbered binds pdf 93
[SYSTEM] 85 binds pdf 94
[SYSTEM] ghost 84 binds pdf 94
[SYSTEM] 86 binds pdf 95
[SYSTEM] ghost 84 binds pdf 95
[SYSTEM] 87 binds pdf 96
[SYSTEM] ghost 84 binds pdf 96
[SYSTEM] 88 binds pdf 97
[SYSTEM] ghost 84 binds pdf 97
[SYSTEM] 89 binds pdf 98
[SYSTEM] ghost 84 binds pdf 98
[SYSTEM] 90 binds pdf 99
[SYSTEM] ghost 84 binds pdf 99
[SYSTEM] 91 binds pdf 100
[SYSTEM] 92 binds pdf 101
[SYSTEM] 93 binds pdf 102
[SYSTEM] 94 binds pdf 103
[SYSTEM] 95 binds pdf 104
[SYSTEM] 96 binds pdf 105
[SYSTEM] 97 binds pdf 106
[SYSTEM] 98 binds pdf 107
[SYSTEM] 99 binds pdf 108
[SYSTEM] 100 binds pdf 109
[SYSTEM] 101 binds pdf 110
[SYSTEM] 102 binds pdf 111
[SYSTEM] 103 binds pdf 112
[SYSTEM] 104 binds pdf 113
[SYSTEM] 105 binds pdf 114
[SYSTEM] 106 binds pdf 115
[SYSTEM] 107 binds pdf 116
[SYSTEM] 108 binds pdf 117
[SYSTEM] 109 binds pdf 118
[SYSTEM] 110 binds pdf 119
[SYSTEM] 111 binds pdf 120
[SYSTEM] 112 binds pdf 121
[SYSTEM] 113 binds pdf 122
[SYSTEM] 114 binds pdf 123
[SYSTEM] 115 binds pdf 124
[SYSTEM] 116 binds pdf 125
[SYSTEM] 117 binds pdf 126
[SYSTEM] 118 binds pdf 127
[SYSTEM] 119 binds pdf 128
[SYSTEM] 120 binds pdf 129
[SYSTEM] 121 binds pdf 130
[SYSTEM] 122 binds pdf 131
[SYSTEM] 123 binds pdf 132
[SYSTEM] 124 binds pdf 133
[SYSTEM] 125 binds pdf 134
[SYSTEM] 126 binds pdf 135
[SYSTEM] 127 binds pdf 136
[SYSTEM] 128 binds pdf 137
[SYSTEM] 129 binds pdf 138
[SYSTEM] 130 binds pdf 139
[SYSTEM] 131 binds pdf 140
[SYSTEM] 132 binds pdf 141
[SYSTEM] 133 binds pdf 142
[SYSTEM] 134 binds pdf 143
[SYSTEM] 135 binds pdf 144
[SYSTEM] 136 binds pdf 145
[SYSTEM] 137 binds pdf 146
[SYSTEM] 138 binds pdf 147
[SYSTEM] 139 binds pdf 148
[SYSTEM] 140 binds pdf 149
[SYSTEM] 141 binds pdf 150
[SYSTEM] 142 binds pdf 151
[SYSTEM] 143 binds pdf 152
[SYSTEM] 144 binds pdf 153
[SYSTEM] 145 binds pdf 154
[SYSTEM] 146 binds pdf 155
[SYSTEM] 147 binds pdf 156
[SYSTEM] 148 binds pdf 157
[SYSTEM] 149 binds pdf 158
[SYSTEM] 150 binds pdf 159
[SYSTEM] 151 binds pdf 160
[SYSTEM] 152 binds pdf 161
[SYSTEM] 153 binds pdf 162
[SYSTEM] 154 binds pdf 163
[SYSTEM] 155 binds pdf 164
[SYSTEM] 156 binds pdf 165
[SYSTEM] 157 binds pdf 166
[SYSTEM] 158 binds pdf 167
[SYSTEM] 159 binds pdf 168
[SYSTEM] 160 binds pdf 169
[SYSTEM] 161 binds pdf 170
[SYSTEM] 162 binds pdf 171
[SYSTEM] 163 binds pdf 172
[SYSTEM] 164 binds pdf 173
[SYSTEM] 165 binds pdf 174
[SYSTEM] 166 binds pdf 175
[SYSTEM] 167 binds pdf 176
[SYSTEM] 168 binds pdf 177
[SYSTEM] 169 binds pdf 178
[SYSTEM] 170 binds pdf 179
[SYSTEM] 171 binds pdf 180
[SYSTEM] 172 binds pdf 181
[SYSTEM] 173 binds pdf 182
[SYSTEM] 174 binds pdf 183
[SYSTEM] 175 binds pdf 184
[SYSTEM] 176 binds pdf 185
[SYSTEM] 177 binds pdf 186
[SYSTEM] 178 binds pdf 187
[SYSTEM] 179 binds pdf 188
[SYSTEM] 180 binds pdf 189
[SYSTEM] 181 binds pdf 190
[SYSTEM] 182 binds pdf 191
[SYSTEM] 183 binds pdf 192
[SYSTEM] 184 binds pdf 193
[SYSTEM] 185 binds pdf 194
[SYSTEM] 186 binds pdf 195
[SYSTEM] 187 binds pdf 196
[SYSTEM] 188 binds pdf 197
[SYSTEM] 189 binds pdf 198
[SYSTEM] 190 binds pdf 199
[SYSTEM] 191 binds pdf 200
[SYSTEM] 192 binds pdf 201
[SYSTEM] 193 binds pdf 202
[SYSTEM] 194 binds pdf 203
[SYSTEM] 195 binds pdf 204
[SYSTEM] 196 binds pdf 205
[SYSTEM] 197 binds pdf 206
[SYSTEM] 198 binds pdf 207
[SYSTEM] 199 binds pdf 208
[SYSTEM] 200 binds pdf 209
[SYSTEM] 201 binds pdf 210
[SYSTEM] 202 binds pdf 211
[SYSTEM] 203 binds pdf 212
[SYSTEM] 204 binds pdf 213
[SYSTEM] 205 binds pdf 214
[SYSTEM] 206 binds pdf 215
[SYSTEM] 207 binds pdf 216
[SYSTEM] 208 binds pdf 217
[SYSTEM] -0 binds pdf 218
[SYSTEM] -1 binds pdf 219
[SYSTEM] -2 binds pdf 220
[SYSTEM] ghost 00 binds pdf 220
[SYSTEM] -3 binds pdf 221
[SYSTEM] -4 binds pdf 222
[SYSTEM] ghost 000 binds pdf 222
[SYSTEM] -5 binds pdf 223
[SYSTEM] -6 binds pdf 224
[SYSTEM] -7 binds pdf 225
[SYSTEM] ghost 0000 binds pdf 225
[SYSTEM] -8 binds pdf 226
[SYSTEM] -9 binds pdf 227
[SYSTEM] -10 binds pdf 228
[SYSTEM] -11 binds pdf 229
[SYSTEM] -12 binds pdf 230
[SYSTEM] -13 binds pdf 231
[SYSTEM] -14 binds pdf 232
[SYSTEM] -15 binds pdf 233
[SYSTEM] -16 binds pdf 234
[SYSTEM] -17 binds pdf 235
[SYSTEM] -18 binds pdf 236
[SYSTEM] -19 binds pdf 237
[SYSTEM] -20 binds pdf 238
[SYSTEM] -21 binds pdf 239
[SYSTEM] -22 binds pdf 240
[SYSTEM] -23 binds pdf 241
[SYSTEM] -24 binds pdf 242
[SYSTEM] -25 binds pdf 243
[SYSTEM] -26 binds pdf 244
[SYSTEM] -27 binds pdf 245
[SYSTEM] -28 binds pdf 246
[SYSTEM] -29 binds pdf 247
[SYSTEM] -30 binds pdf 248
[SYSTEM] -31 binds pdf 249
[SYSTEM] -32 binds pdf 250
[SYSTEM] -33 binds pdf 251
[SYSTEM] -34 binds pdf 252
[SYSTEM] -35 binds pdf 253
[SYSTEM] -36 binds pdf 254
[SYSTEM] -37 binds pdf 255
[SYSTEM] -38 binds pdf 256
[SYSTEM] -39 binds pdf 257
[SYSTEM] -40 binds pdf 258
[SYSTEM] -41 binds pdf 259
[SYSTEM] -42 binds pdf 260
[SYSTEM] -43 binds pdf 261
[SYSTEM] -44 binds pdf 262
[SYSTEM] -45 binds pdf 263
[SYSTEM] -46 binds pdf 264
[SYSTEM] -47 binds pdf 265
[SYSTEM] bind close labels 265 ghosts 9 wrote toc_bind.tsv
dylanmccapes@heuristic-friction:~/dev/REALITY_USER_MANUAL$
```
