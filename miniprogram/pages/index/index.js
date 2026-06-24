// 家庭私厨 — web-view 页面

Page({
  data: {
    webUrl: ''
  },

  onLoad() {
    const app = getApp();
    const serverUrl = app.globalData.serverUrl;
    this.setData({
      webUrl: serverUrl
    });
    console.log('[家庭私厨] web-view 加载:', serverUrl);
  },

  onWebLoad(e) {
    console.log('[家庭私厨] web-view 加载成功', e.detail);
  },

  onWebError(e) {
    console.error('[家庭私厨] web-view 加载失败', e.detail);
    wx.showToast({
      title: '页面加载失败，请检查网络',
      icon: 'none',
      duration: 3000
    });
  },

  onMessage(e) {
    console.log('[家庭私厨] 收到 Web 消息:', e.detail.data);
  }
});
