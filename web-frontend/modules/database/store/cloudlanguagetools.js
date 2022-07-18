import CloudLanguageToolsService from '@baserow/modules/database/services/cloudlanguagetools'
// import { clone } from '@baserow/modules/core/utils/object'

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
    const { data } = await CloudLanguageToolsService(this.$client).fetchAllLanguages()
    let languagesArray = [];
    for (const language_id in data) {
        languagesArray.push({
        id: language_id,
        name: data[language_id]
        });
    }
    commit('SET_ALL_LANGUAGES', languagesArray);
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
