from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import numpy


def run_scene():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(300, 300)
    glutCreateWindow("Sphere")
    glutHideWindow()

    glClearColor(0., 0., 0., 0.)
    glClearDepth(1.)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)

    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40, 1, 1, 500)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0, 0, 0,
              0, 0, 1,
              0, 1, 0)
    glPushMatrix()

    draw_sphere()


def draw_sphere():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    texture_id = read_texture()

    glTranslatef(0., 0., 0.)
    glScalef(-1, 1, 1)

    x, y, z = (0, 0, 0)
    glRotatef(x, 1., 0., 0.)
    glRotatef(y, 0., 1., 0.)
    glRotatef(z, 0., 0., 1.)

    glEnable(GL_TEXTURE_2D)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glEnable(GL_TEXTURE_GEN_S)
    glEnable(GL_TEXTURE_GEN_T)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glutSolidSphere(18, 200, 100)
    glDisable(GL_TEXTURE_2D)

    buf = glReadPixels(0, 0, 300, 300, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=(300, 300), data=buf)
    image.show()

    glPopMatrix()
    glutSwapBuffers()


def read_texture(filename=os.path.dirname(os.path.realpath(__file__)) + '/pano.jpg'):
    img = Image.open(filename)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id


if __name__ == '__main__':
    run_scene()
