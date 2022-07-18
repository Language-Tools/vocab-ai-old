import CloudLanguageToolsService from '@baserow/modules/database/services/cloudlanguagetools'

export const state = () => ({
  allLanguages: [],
})

export const mutations = {
  SET_ALL_LANGUAGES(state, allLanguages) {
    state.allLanguages = allLanguages;
  }
}

export const actions = {
  /**
   * Fetches all the fields of a given table. The is mostly called when the user
   * selects a different table.
   */
  async fetchAllLanguages({ commit, getters, dispatch }, table) {
    console.log('store/cloudlanguagetools fetchAllLanguages');
    return new Promise((resolve, reject) => {
        // const { data } = await CloudLanguageToolsService(this.$client).fetchAllLanguages()
        CloudLanguageToolsService(this.$client).fetchAllLanguages().then((response) => {
            let languagesArray = [];
            for (const language_id in response.data) {
                languagesArray.push({
                id: language_id,
                name: response.data[language_id]
                });
            }
            commit('SET_ALL_LANGUAGES', languagesArray);
            resolve();
        });
    });
  }
}

export const getters = {
    allLanguages(state) {
        return state.allLanguages;
    }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
