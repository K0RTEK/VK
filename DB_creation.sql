create database VK;
create table user_vk_group
(
    user_id     int, --id пользователя
    vk_group_id int  --id группы, на которую подписан пользователь
);

create table vk_group_id_topic
(
    vk_group_id int,         --id группы
    topic_group varchar(255) --тематика группы

);

create table user_vk_characteristic
(
    user_id         int,         --id пользователя
    user_posts_date timestamp,   --даты публикации постов на странице пользователя
    topic_user      varchar(255) --тематика постов на странице пользователя
