import { defineStore } from "pinia";

const initialPosts = [
  {
    id: 1,
    category: "예금/적금",
    title: "사회초년생인데 월 50만원 적금 추천해주세요",
    content: "월급에서 매달 50만원 정도 저축하려고 합니다. 금리 높은 적금이나 자유적금 중에 뭐가 좋을까요?",
    author: "이윤서",
    comments: 4,
    views: 128,
    likes: 12,
    createdAt: "2시간 전",
    tags: ["사회초년생", "목돈모으기", "적금"],
    commentList: [
      { id: 1, author: "김민지", content: "저도 비슷한 고민 중인데 참고할게요!", createdAt: "1시간 전" },
      { id: 2, author: "박지훈", content: "요즘은 금리 비교 먼저 해보는 게 좋은 것 같아요.", createdAt: "30분 전" }
    ]
  },
  {
    id: 2,
    category: "카드",
    title: "교통비 많이 쓰는 사람한테 좋은 체크카드 있을까요?",
    content: "대중교통이랑 카페 사용이 많은 편이라 할인율 좋은 카드를 찾고 있어요.",
    author: "김민지",
    comments: 7,
    views: 203,
    likes: 18,
    createdAt: "5시간 전",
    tags: ["체크카드", "교통비", "카페할인"],
    commentList: [
      { id: 1, author: "정우진", content: "교통비는 월 사용금액 조건을 먼저 보는 게 좋더라고요.", createdAt: "3시간 전" },
      { id: 2, author: "최하은", content: "카페 할인까지 같이 보면 생활비 카드로도 괜찮겠네요.", createdAt: "2시간 전" }
    ]
  },
  {
    id: 3,
    category: "대출",
    title: "전세대출 처음 알아보는데 뭐부터 봐야 하나요?",
    content: "전세 계약을 앞두고 있는데 금리, 한도, 보증보험 같은 게 너무 어렵네요.",
    author: "박지훈",
    comments: 9,
    views: 341,
    likes: 25,
    createdAt: "어제",
    tags: ["전세대출", "금리", "초보"],
    commentList: [
      { id: 1, author: "이윤서", content: "은행별 한도랑 보증기관 조건을 같이 봐야 해요.", createdAt: "어제" },
      { id: 2, author: "김민지", content: "계약 전에 사전심사부터 받아보는 걸 추천해요.", createdAt: "어제" }
    ]
  },
  {
    id: 4,
    category: "ETF/주식",
    title: "적금 대신 ETF를 조금씩 사는 건 어떤가요?",
    content: "매달 20만원씩 장기 투자하려고 하는데 적금이랑 ETF 중에 고민입니다.",
    author: "최하은",
    comments: 11,
    views: 512,
    likes: 33,
    createdAt: "어제",
    tags: ["ETF", "장기투자", "월적립"],
    commentList: [
      { id: 1, author: "박지훈", content: "목표 기간이 길면 일부는 ETF도 괜찮지만 비상금은 예금이 좋아요.", createdAt: "어제" },
      { id: 2, author: "정우진", content: "가격 변동을 버틸 수 있는 돈인지 먼저 나눠보세요.", createdAt: "20시간 전" }
    ]
  },
  {
    id: 5,
    category: "청약",
    title: "청약통장 납입금액 10만원 유지하는 게 맞나요?",
    content: "청약통장 만든 지 얼마 안 됐는데 매달 얼마씩 넣는 게 좋은지 궁금합니다.",
    author: "정우진",
    comments: 3,
    views: 95,
    likes: 8,
    createdAt: "3일 전",
    tags: ["청약", "청약통장", "내집마련"],
    commentList: [
      { id: 1, author: "이윤서", content: "공공분양까지 생각하면 10만원 유지가 많이 추천돼요.", createdAt: "2일 전" },
      { id: 2, author: "최하은", content: "지역과 목표 주택 유형에 따라 달라서 같이 확인해보세요.", createdAt: "1일 전" }
    ]
  }
];

export const communityCategories = ["전체", "예금/적금", "카드", "대출", "ETF/주식", "청약", "질문"];
export const writeCategories = ["예금/적금", "카드", "대출", "ETF/주식", "청약", "질문"];

export const useCommunityStore = defineStore("community", {
  state: () => ({
    posts: initialPosts.map(post => ({
      ...post,
      liked: false,
      tags: [...post.tags],
      commentList: [...post.commentList]
    }))
  }),
  getters: {
    filteredPosts: state => category => {
      if (!category || category === "전체") return state.posts;
      return state.posts.filter(post => post.category === category);
    },
    getPostById: state => id => state.posts.find(post => Number(post.id) === Number(id)),
    popularPosts: state => [...state.posts].sort((a, b) => b.likes + b.comments - (a.likes + a.comments)).slice(0, 3)
  },
  actions: {
    addPost(post) {
      const nextId = this.posts.length ? Math.max(...this.posts.map(item => item.id)) + 1 : 1;
      const nextPost = {
        id: nextId,
        category: post.category,
        title: post.title,
        content: post.content,
        author: post.author || "FinPick 사용자",
        comments: 0,
        views: 0,
        likes: 0,
        liked: false,
        createdAt: "방금 전",
        tags: post.tags || [],
        commentList: []
      };
      this.posts.unshift(nextPost);
      return nextPost;
    },
    increaseViews(id) {
      const post = this.getPostById(id);
      if (post) post.views += 1;
    },
    toggleLike(id) {
      const post = this.getPostById(id);
      if (!post) return;
      post.liked = !post.liked;
      post.likes += post.liked ? 1 : -1;
    },
    addComment(id, comment) {
      const post = this.getPostById(id);
      if (!post) return;
      const nextId = post.commentList.length ? Math.max(...post.commentList.map(item => item.id)) + 1 : 1;
      post.commentList.push({
        id: nextId,
        author: comment.author || "FinPick 사용자",
        content: comment.content,
        createdAt: "방금 전",
        userKey: comment.userKey || null,
        profileImage: comment.profileImage || ""
      });
      post.comments += 1;
    },
    updateComment(postId, commentId, content) {
      const post = this.getPostById(postId);
      if (!post) return;
      const comment = post.commentList.find(item => Number(item.id) === Number(commentId));
      if (!comment) return;
      comment.content = content;
      comment.updatedAt = "수정됨";
    },
    deleteComment(postId, commentId) {
      const post = this.getPostById(postId);
      if (!post) return;
      const beforeCount = post.commentList.length;
      const nextComments = post.commentList.filter(item => Number(item.id) !== Number(commentId));
      post.commentList = nextComments;
      if (nextComments.length < beforeCount) post.comments = Math.max(0, post.comments - 1);
    }
  }
});



