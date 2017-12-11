from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import numpy


class Sphere(object):
    def __init__(self, size, f=None):
        self._w, self._h = size
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self._w, self._h)
        glutCreateWindow("Sphere")
        glutHideWindow()

        glClearColor(0., 0., 0., 0.)
        glClearDepth(1.)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)

        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(40, self._w * 1.0 / self._h, 1.0, 500.0)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0,
                  0, 0, 1,
                  0, 1, 0)
        glPushMatrix()

        if f is None:
            f = os.path.dirname(os.path.realpath(__file__)) + '/pano.jpg'
        self._read_texture(f)

    def draw_sphere(self, *args):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glTranslatef(0., 0., 0.)
        glScalef(-1, 1, 1)

        x, y, z = args
        glRotatef(x, 1., 0., 0.)
        glRotatef(y, 0., 1., 0.)
        glRotatef(z, 0., 0., 1.)

        glEnable(GL_TEXTURE_2D)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
        glBindTexture(GL_TEXTURE_2D, self._texture_id)

        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glutSolidSphere(18, 200, 100)
        glDisable(GL_TEXTURE_2D)

        buf = glReadPixels(0, 0, self._w, self._h, GL_RGB, GL_UNSIGNED_BYTE)

        glPopMatrix()
        glutSwapBuffers()
        return buf

    def output(self, d, subd):
        for k, vec in d.iteritems():
            buf = self.draw_sphere(*vec)
            image = Image.frombytes(mode="RGB", size=(self._w, self._h), data=buf)
            # image.save(subd + "/%s.jpg" % k)
            image.show()

    def _read_texture(self, filename):
        img = Image.open(filename)
        img_data = numpy.array(list(img.getdata()), numpy.int8)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                     GL_RGB, GL_UNSIGNED_BYTE, img_data)
        self._texture_id = texture_id


def _test():
    s = Sphere((600, 300))
    s.output({
        'top': (180, 180, 0),
        'bottom': (0, 180, 0),
        'front': (90, 180, 0),
        'left': (90, 180, 90),
        'back': (90, 180, 180),
        'right': (90, 180, 270),
    }, os.path.dirname(os.path.realpath(__file__)))


if __name__ == '__main__':
    _test()
