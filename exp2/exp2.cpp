#include <iostream>
#include <vector>
#include <queue>
#include <map>
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
    Bitmap() : M(NULL), N(0), _sz(0) { init(8); }
    ~Bitmap() {
        if (M != NULL) { delete[] M; M = NULL; }
        _sz = 0; N = 0;
    }

    void init(Rank n) {
        if (M != NULL) delete[] M;
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
        for (Rank i = 0; i < n; i++)
            s[i] = test(i) ? '1' : '0';
        s[n] = '\0';
        return s;
    }
};

struct HuffNode {
    char data;
    int weight;
    HuffNode *left, *right, *parent;

    HuffNode(char c = '\0', int w = 0) 
        : data(c), weight(w), left(NULL), right(NULL), parent(NULL) {}

    struct Compare {
        bool operator()(const HuffNode* a, const HuffNode* b) {
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
        length = other.length;
        for (int i = 0; i < length; i++)
            if (other.bits.test(i)) bits.set(i);
            else bits.clear(i);
    }

    void appendBit(bool isOne) {
        if (isOne) bits.set(length);
        else bits.clear(length);
        length++;
    }

    friend ostream& operator<<(ostream& os, const HuffCode& code) {
        char* s = code.bits.bits2string(code.length);
        if (s != NULL) { os << s; delete[] s; }
        return os;
    }

    int getLength() const { return length; }
    const Bitmap& getBits() const { return bits; }
};

struct NodeCode {
    HuffNode* node;
    HuffCode code;
    NodeCode(HuffNode* n = NULL, const HuffCode& c = HuffCode()) 
        : node(n), code(c) {}
};

class HuffmanCoder {
private:
    HuffNode* root;
    map<char, int> freqMap;
    map<char, HuffCode> codeMap;

    void countFrequency(const string& text) {
        freqMap.clear();
        for (size_t i = 0; i < text.size(); i++) {
            char c = text[i];
            freqMap[c]++;
        }
        cout << "[统计完成] 共 " << freqMap.size() << " 种不同字符" << endl;
    }
    void buildTree() {
        priority_queue<HuffNode*, vector<HuffNode*>, HuffNode::Compare> pq;

        for (map<char, int>::iterator it = freqMap.begin(); it != freqMap.end(); ++it) {
            pq.push(new HuffNode(it->first, it->second));
        }

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
        cout << "[树构建完成] Huffman树根节点" << (root ? "存在" : "不存在") << endl;
    }
    void generateCodes() {
        codeMap.clear();
        if (root == NULL) return;

        queue<NodeCode> q;
        q.push(NodeCode(root, HuffCode()));

        while (!q.empty()) {
            NodeCode current = q.front(); q.pop();
            HuffNode* node = current.node;
            HuffCode code = current.code;

            if (node->left == NULL && node->right == NULL) {
                codeMap[node->data] = code;
                continue;
            }

            if (node->left != NULL) {
                HuffCode leftCode = code;
                leftCode.appendBit(false);
                q.push(NodeCode(node->left, leftCode));
            }
            if (node->right != NULL) {
                HuffCode rightCode = code;
                rightCode.appendBit(true);
                q.push(NodeCode(node->right, rightCode));
            }
        }
    }

public:
    HuffmanCoder(const string& text) {
        root = NULL;
        countFrequency(text);
        buildTree();
        generateCodes();
    }

    ~HuffmanCoder() {
        if (root == NULL) return;
        queue<HuffNode*> q;
        q.push(root);
        while (!q.empty()) {
            HuffNode* node = q.front(); q.pop();
            if (node->left != NULL) q.push(node->left);
            if (node->right != NULL) q.push(node->right);
            delete node;
        }
        root = NULL;
    }

    void printTables() {
        cout << "\n===== 字符频率表 =====" << endl;
        for (map<char, int>::iterator it = freqMap.begin(); it != freqMap.end(); ++it) {
            cout << "字符: '";
            if (it->first == ' ') cout << "空格";
            else cout << it->first;
            cout << "'\t频率: " << it->second << endl;
        }

        cout << "\n===== Huffman编码表 =====" << endl;
        for (map<char, HuffCode>::iterator it = codeMap.begin(); it != codeMap.end(); ++it) {
            cout << "字符: '";
            if (it->first == ' ') cout << "空格";
            else cout << it->first;
            cout << "'\t编码: " << it->second 
                 << "\t长度: " << it->second.getLength() << endl;
        }
    }
    HuffCode encodeWord(const string& word) {
        HuffCode res;
        cout << "\n[日志] 编码单词：" << word << endl;
        for (size_t i = 0; i < word.size(); i++) {
            char c = word[i];
            if (codeMap.find(c) == codeMap.end()) {
                cout << "[警告] 字符 '" << c << "' 不在编码表中，跳过" << endl;
                continue;
            }
            HuffCode charCode = codeMap[c];
            char* bits = charCode.getBits().bits2string(charCode.getLength());
            if (bits != NULL) {
                for (int j = 0; j < charCode.getLength(); j++) {
                    res.appendBit(bits[j] == '1');
                }
                delete[] bits;
            }
        }
        return res;
    }
};

int main() {
    string text = 
        "I am happy to join with you today in what will go down in history as the greatest demonstration for freedom in the history of our nation.\n"
        "Five score years ago, a great American, in whose symbolic shadow we stand today, signed the Emancipation Proclamation. This momentous decree came as a great beacon light of hope to millions of Negro slaves, who had been seared in the flames of withering injustice. It came as a joyous day-break to end the long night of their captivity.";

    HuffmanCoder coder(text);
    coder.printTables();
    string word = "dream";
    HuffCode wordCode = coder.encodeWord(word);
    cout << "\n最终结果：" << endl;
    cout << "单词 \"" << word << "\" 的Huffman编码：" << wordCode << endl;
    cout << "编码长度：" << wordCode.getLength() << " 比特" << endl;

    cout << endl;
    system("pause");
    return 0;
}
