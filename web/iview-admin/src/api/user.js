/* eslint-disable */
import axios from '@/libs/api.request'
import {API_PREFIX} from './constants'

export const login = ({ username, password }) => {
  const data = {
    username,
    password
  }
  console.log("Start request")
  let result= axios.request({
    url: 'account/login/',
    data,
    method: 'post'
  })
  console.log("End request")
  return result
}

export const getUserInfo = (token) => {
  console.log("TOken ",token)
  return axios.request({
    url: 'account/',
    params: {
     id:token
    },
    method: 'get'
  })
}

export const logout = (token) => {
  return axios.request({
    url: 'account/logout/',
    method: 'post'
  })
}

export const getUnreadCount = () => {
  return axios.request({
    url: 'message/count',
    method: 'get'
  })
}

export const getMessage = () => {
  return axios.request({
    url: 'message/init',
    method: 'get'
  })
}

export const getContentByMsgId = msg_id => {
  return axios.request({
    url: 'message/content',
    method: 'get',
    params: {
      msg_id
    }
  })
}

export const hasRead = msg_id => {
  return axios.request({
    url: 'message/has_read',
    method: 'post',
    data: {
      msg_id
    }
  })
}

export const removeReaded = msg_id => {
  return axios.request({
    url: 'message/remove_readed',
    method: 'post',
    data: {
      msg_id
    }
  })
}

export const restoreTrash = msg_id => {
  return axios.request({
    url: 'message/restore',
    method: 'post',
    data: {
      msg_id
    }
  })
}
