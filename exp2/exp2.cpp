#include <iostream>
#include <vector>
#include <queue>
#include <cstring>
#include <cctype>
#include <utility>
using namespace std;

class Bitmap {
public:
    typedef size_t Rank;
private:
    unsigned char* M;
    Rank N, _sz;

    void expand(Rank k) {
        if (k < 8 * N) return;
        Rank oldN = N;
        unsigned char* oldM = M;
        N = (2 * k + 7) / 8;
        M = new unsigned char[N];
        memset(M, 0, N);
        if (oldM != NULL) {
            memcpy(M, oldM, oldN);
            delete[] oldM;
        }
    }
public:
    Bitmap() : M(NULL), N(0), _sz(0) {
        init(8);
    }

    ~Bitmap() {
        if (M != NULL) {
            delete[] M;
            M = NULL;
        }
        _sz = 0;
        N = 0;
    }

    void init(Rank n) {
        if (M != NULL) {
            delete[] M;
            M = NULL;
        }
        N = (n + 7) / 8;
        M = new unsigned char[N];
        memset(M, 0, N);
        _sz = 0;
    }

    void set(Rank k) {
        expand(k);
        if (!test(k)) {
            M[k >> 3] |= (0x80 >> (k & 0x07));
            _sz++;
        }
    }

    void clear(Rank k) {
        expand(k);
        if (test(k)) {
            M[k >> 3] &= ~(0x80 >> (k & 0x07));
            _sz--;
        }
    }

    bool test(Rank k) const {
        if (k >= 8 * N || M == NULL) return false;
        return (M[k >> 3] & (0x80 >> (k & 0x07))) != 0;
    }

    char* bits2string(Rank n) const {
        if (M == NULL) return NULL;
        char* s = new char[n + 1];
        memset(s, 0, n + 1);
        for (Rank i = 0; i < n; i++) {
            s[i] = test(i) ? '1' : '0';
        }
        s[n] = '\0';
        return s;
    }
};

class BinTree {
public:
    pair<char, int> data;
    BinTree* left;
    BinTree* right;
    BinTree* parent;

    BinTree(char c = '\0', int w = 0) 
        : data(make_pair(c, w)), left(NULL), right(NULL), parent(NULL) {}
    
    virtual ~BinTree() {
        if (left != NULL) {
            delete left;
            left = NULL;
        }
        if (right != NULL) {
            delete right;
            right = NULL;
        }
        parent = NULL;
    }
};

struct HuffNode : public BinTree {
    int weight;

    HuffNode(char c = '\0', int w = 0) : BinTree(c, w), weight(w) {}

    struct Compare {
        bool operator()(const HuffNode* a, const HuffNode* b) {
            if (a == NULL || b == NULL) return false;
            return a->weight > b->weight;
        }
    };
};

class HuffCode {
private:
    Bitmap bits;
    int length;
public:
    HuffCode() : length(0) {}
    HuffCode(const HuffCode& other) {
        this->length = other.length;
        for (int i = 0; i < other.length; i++) {
            if (other.bits.test(i)) {
                this->bits.set(i);
            } else {
                this->bits.clear(i);
            }
        }
    }
    HuffCode& operator=(const HuffCode& other) {
        if (this == &other) return *this;
        this->length = other.length;
        for (int i = 0; i < this->length; i++) {
            this->bits.clear(i);
        }
        for (int i = 0; i < other.length; i++) {
            if (other.bits.test(i)) {
                this->bits.set(i);
            }
        }
        return *this;
    }

    void appendBit(bool isOne) {
        if (isOne) bits.set(length);
        else bits.clear(length);
        length++;
    }

    friend ostream& operator<<(ostream& os, const HuffCode& code) {
        char* s = code.bits.bits2string(code.length);
        if (s != NULL) {
            os << s;
            delete[] s;
        }
        return os;
    }

    int getLength() const { return length; }
    const Bitmap& getBits() const { return bits; }
};

struct NodeCode {
    HuffNode* node;
    HuffCode code;
    NodeCode(HuffNode* n = NULL, const HuffCode& c = HuffCode()) {
        node = n;
        code = c;
    }
};
class HuffmanCoder {
private:
    HuffNode* root;
    vector<int> freqTable;
    vector<HuffCode> codeTable;

    vector<int> countFreq(const string& text) {
        vector<int> freq(26, 0);
        if (text.empty()) {
            freq['d'-'a'] = 5;
            freq['r'-'a'] = 3;
            freq['e'-'a'] = 8;
            freq['a'-'a'] = 10;
            freq['m'-'a'] = 2;
            freqTable = freq;
            return freq;
        }

        for (size_t i = 0; i < text.size(); i++) {
            char c = text[i];
            if (isalpha(c)) {
                char lowerC = tolower(c);
                freq[lowerC - 'a']++;
            }
        }

        bool allZero = true;
        for (int i = 0; i < 26; i++) {
            if (freq[i] > 0) {
                allZero = false;
                break;
            }
        }
        if (allZero) {
            freq['d'-'a'] = 5;
            freq['r'-'a'] = 3;
            freq['e'-'a'] = 8;
            freq['a'-'a'] = 10;
            freq['m'-'a'] = 2;
        }

        freqTable = freq;
        return freq;
    }

    void buildTree(const vector<int>& freq) {
        priority_queue<HuffNode*, vector<HuffNode*>, HuffNode::Compare> pq;

        int leafCount = 0;
        for (int i = 0; i < 26; i++) {
            if (freq[i] > 0) {
                pq.push(new HuffNode('a' + i, freq[i]));
                leafCount++;
            }
        }
        cout << "[日志] 叶子节点数量：" << leafCount << endl;

        while (pq.size() > 1) {
            HuffNode* left = pq.top(); pq.pop();
            HuffNode* right = pq.top(); pq.pop();
            
            HuffNode* parent = new HuffNode('\0', left->weight + right->weight);
            parent->left = left;
            parent->right = right;
            left->parent = parent;
            right->parent = parent;
            
            pq.push(parent);
        }

        root = pq.empty() ? NULL : pq.top();
        cout << "[日志] Huffman树根节点：" << (root == NULL ? "NULL" : "正常") << endl;
    }

    void genCode() {
        if (root == NULL) return;
        queue<NodeCode> q;
        q.push(NodeCode(root, HuffCode()));

        while (!q.empty()) {
            NodeCode current = q.front(); q.pop();
            HuffNode* node = current.node;
            HuffCode code = current.code;

            if (node->left == NULL && node->right == NULL) {
                char c = node->data.first;
                codeTable[c - 'a'] = code;
                cout << "[日志] 生成字符 '" << c << "' 编码：" << code << endl;
                continue;
            }

            if (node->left != NULL) {
                HuffCode leftCode = code;
                leftCode.appendBit(false);
                q.push(NodeCode((HuffNode*)node->left, leftCode));
            }
            if (node->right != NULL) {
                HuffCode rightCode = code;
                rightCode.appendBit(true);
                q.push(NodeCode((HuffNode*)node->right, rightCode));
            }
        }
    }

public:
    HuffmanCoder(const string& text = "") {
        codeTable.resize(26);
        freqTable.resize(26, 0);
        root = NULL;
        vector<int> freq = countFreq(text);
        buildTree(freq);
        genCode();
    }

    ~HuffmanCoder() {
        if (root != NULL) {
            delete root;
            root = NULL;
        }
    }

    HuffCode encode(const string& word) {
        HuffCode res;
        cout << "[日志] 编码单词：" << word << endl;
        for (size_t i = 0; i < word.size(); i++) {
            char c = word[i];
            if (!isalpha(c)) continue;
            int idx = tolower(c) - 'a';
            if (idx < 0 || idx >= 26) continue;
            if (codeTable[idx].getLength() == 0) {
                cout << "[警告] 字符 '" << c << "' 无编码！" << endl;
                continue;
            }
            char* s = codeTable[idx].getBits().bits2string(codeTable[idx].getLength());
            if (s == NULL) continue;
            for (int j = 0; j < codeTable[idx].getLength(); j++) {
                res.appendBit(s[j] == '1');
            }
            delete[] s;
        }
        return res;
    }

    void printTable() {
        cout << "\n===== Huffman编码表 =====" << endl;
        cout << "字符\t频率\t编码" << endl;
        cout << "------------------------" << endl;
        int count = 0;
        for (int i = 0; i < 26; i++) {
            if (codeTable[i].getLength() > 0) {
                char c = 'a' + i;
                cout << c << "\t" << freqTable[i] << "\t" << codeTable[i] << endl;
                count++;
            }
        }
        if (count == 0) {
            cout << "（无有效编码）" << endl;
        }
        cout << "========================" << endl;
        cout.flush();
    }
};
int main() {
    ios::sync_with_stdio(true);
    cin.tie(NULL);

    HuffmanCoder coder;
    coder.printTable();
    
    string word = "dream";
    HuffCode code = coder.encode(word);
    cout << "\n最终结果：" << endl;
    cout << "单词 \"" << word << "\" 的Huffman编码：" << code << endl;
    cout << "编码长度：" << code.getLength() << " 比特" << endl;

    cout.flush();
    return 0;
}
